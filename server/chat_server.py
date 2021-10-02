import logging
import socketio as socketio_client
import sys
from flask import Flask, request
from flask_socketio import SocketIO
from server import Server, get_local_ip


# Server
app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.disabled = True
socketio = SocketIO(app)
sio_client = socketio_client.Client()
rel_client = socketio_client.Client()


# Write server feedback on '.logs' file
def fprint(text):
    with open('.logs', 'a') as logfile:
        print(text, file=logfile)


# Broadcast queued messages
def broadcast_past_messages(sid=None):
    if sid is not None:  # Send messages to specific client
        socketio.emit('msg_queue', sv.messages, room=sid)
    else:  # Send messages to everyone
        socketio.emit('msg_queue', sv.messages, broadcast=True)


# Obtain ip/port/id for private messaging and tell client to use p2p
def private(username_target, username_sender):
    ip, port, node_id = sv.get_user_connections(username_target)
    socketio.emit('send_private_msg', {
        'ip': ip, 'port': port, 'id': node_id,
        'sender': username_sender, 'target': username_target}, room=request.sid)


# Revert server to initial state
def reset_server(new_n):
    print(f'Resetting server with N = {new_n} users required')
    socketio.emit('exit', broadcast=True)
    sv.set_params(n_clients=new_n)


# Parse & delegate different commands
def command_handler(msg):
    message = msg.strip().split()
    if not message:  # Empty message
        res = 'Messages can\'t be empty!'
        socketio.emit('event', res, room=request.sid)
        return True
    if message[0] == '$private':  # Private command
        if len(message) < 2:
            res = 'Invalid format for private message! Use: $private USER MSG'
            socketio.emit('event', res, room=request.sid)
            return True
        username = message[1]
        if username not in (sv.usernames - set(sv[request.sid])):
            res = 'Invalid username for private message!'
            socketio.emit('event', res, room=request.sid)
            return True
        private(username, sv[request.sid])
        return True
    if message[0] == '$reset':  # Reset command
        try:
            new_n = int(message[1][1:])
            reset_server(new_n)
        except (IndexError, ValueError):
            res = 'Invalid format for reset! Use: $reset -N'
            socketio.emit('event', res, room=request.sid)
        return True
    return False


# ************************** Socket Events **************************

# Listen for messages
@socketio.on('message')
def handle_message(data):
    # Parse message
    if not command_handler(data):
        # Normal message: "USERNAME: MESSAGE"
        message = f'{sv[request.sid]}: {data}'
        sv.messages_lock.acquire()
        sv.messages.append(message)
        sv.messages_lock.release()

        # Broadcast message
        if sv.n_clients >= sv.N_CLIENTS_REQUIRED:
            socketio.emit('response', message, broadcast=True)


# Process login for each user
@socketio.on('login')
def handle_login(data):
    # Check old users
    c_data = f'{data["ip"]}:{data["port"]}'
    if c_data in sv.old_users:
        user = sv.old_users[c_data]
        sv.build_user(user, request.sid, data['ip'], data['port'], data['id'])
        if sv.n_clients == sv.N_CLIENTS_REQUIRED:
            print('Chat is now active!')
            broadcast_past_messages()
            sv.N_CLIENTS_REQUIRED = -1  # Chat is permanent from now on
        return

    # Check new users
    user = data['user']

    # Invalid username
    if (not user) or (':' in user) or (' ' in user):
        socketio.emit('denied', 'Invalid username!', room=request.sid)
        return

    # New user
    if user not in sv.usernames:
        sv.build_user(user, request.sid, data['ip'], data['port'], data['id'])
        socketio.emit('users', sv.n_clients, broadcast=True)
        socketio.emit('accepted', room=request.sid)
    else:  # Login failed
        socketio.emit('denied', f'{user} is already in use!', room=request.sid)
        return

    # Check if N required clients have joined
    join_msg = f'{user} has joined the chat!'
    sv.messages_lock.acquire()
    sv.messages.append(join_msg)
    sv.messages_lock.release()
    if sv.n_clients == sv.N_CLIENTS_REQUIRED:
        print('Chat is now active!')
        broadcast_past_messages()
        sv.N_CLIENTS_REQUIRED = -1  # Chat is permanent from now on
    elif sv.n_clients > sv.N_CLIENTS_REQUIRED:
        broadcast_past_messages(request.sid)
        socketio.emit('response', join_msg, broadcast=True,
                      include_self=False)


# User disconnects
@socketio.on('disconnect')
def disconnect():
    user = sv.users.pop(request.sid, False)
    if user and not sv.migrating:
        username = user.username
        sv.n_clients -= 1
        sv.usernames.remove(username)
        socketio.emit(
            'users', sv.n_clients, broadcast=True, include_self=False)
        msg = f'{username} has left the chat!'
        if sv.n_clients > sv.N_CLIENTS_REQUIRED:
            socketio.emit('response', msg)
        sv.messages_lock.acquire()
        sv.messages.append(msg)
        sv.messages_lock.release()


# Migrate to new server
@socketio.on('migrate')
def migrate(data):
    sv.migrator.migrate_data(data, request.sid)


# Prepare new server
@sio_client.on('prepare')
def prepare(data):
    sv.old_users = data['users']
    sv.messages_lock.acquire()
    sv.messages = data['messages']
    sv.messages_lock.release()
    sv.client.emit('ready')
    sv.relay_client.emit('register', [sv.ip, sv.port])
    print('\nFinished receiving data from previous server!\n')
    sv.migrator.timer.start()


# Last server is closing
@sio_client.on('closing')
def closing():
    sv.client.disconnect()


# New server is ready
@socketio.on('ready')
def ready():
    print('\nFinished migrating, exiting server...\n')
    sv.sio.emit('closing', room=request.sid)
    sv.relay_client.disconnect()
    sv.sio.emit('reconnect', sv.new_server)
    sv.sio.stop()

# *******************************************************************


# Run chat server
if __name__ == '__main__':
    # fprint('Init server...')
    server_n = int(sys.argv[1][1:])
    server_port = sys.argv[2]
    server_type = sys.argv[3]
    local_ip = get_local_ip()
    if server_type == 'original':
        relay = f'http://{local_ip}:{5000}'
    else:
        relay = sys.argv[5]
    # fprint(f'Server relay: {relay}')
    sv = Server(local_ip, server_port, socketio, sio_client, rel_client, relay,
                start=server_type != 'new')
    sv.N_CLIENTS_REQUIRED = server_n
    if server_type == 'new':
        sv.relay_client.connect(sv.relay)
        old_server = sys.argv[4]
        old_server_uri = f'http://{old_server}'
        sv.old_server = old_server_uri
        sv.client.connect(old_server_uri)
        new_server = f'http://{sv.ip}:{sv.port}'
        sv.client.emit('migrate', new_server)
    try:
        # fprint(f'Running server on port {server_port}')
        socketio.run(app, host='0.0.0.0', port=server_port)
    except KeyboardInterrupt:
        # fprint('KeyboardInterrupt')
        pass
    finally:
        # fprint('Shutting down server\n')
        exit()
