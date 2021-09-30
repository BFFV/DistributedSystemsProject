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
        sv.messages.append(message)

        # Broadcast message
        if sv.n_clients >= sv.N_CLIENTS_REQUIRED:
            socketio.emit('response', message, broadcast=True)


# Process login for each user
@socketio.on('login')
def handle_login(data):
    user = data['user']

    # Invalid username
    if (':' in user) or (' ' in user):
        socketio.emit('denied', 'Invalid username!', room=request.sid)
        return

    # New user
    # TODO: If user ip/port is old, then don't tell him anything (transparent)
    if user not in sv.usernames:
        sv.build_user(user, request.sid, data['ip'], data['port'], data['id'])
        socketio.emit('users', sv.n_clients, broadcast=True)
        socketio.emit('accepted', room=request.sid)
    else:  # Login failed
        socketio.emit('denied', f'{user} is already in use!', room=request.sid)
        return

    # Check if N required clients have joined
    join_msg = f'{user} has joined the chat!'
    sv.messages.append(join_msg)
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
    if user:
        username = user.username
        sv.n_clients -= 1
        sv.usernames.remove(username)
        socketio.emit(
            'users', sv.n_clients, broadcast=True, include_self=False)
        msg = f'{username} has left the chat!'
        if sv.n_clients > sv.N_CLIENTS_REQUIRED:
            socketio.emit('response', msg)
        sv.messages.append(msg)


# Migrate to new server
@socketio.on('migrate')
def migrate(data):
    sv.migrator.migrate_data(data)


# Prepare new server
@socketio.on('prepare')
def prepare(data):
    print(data)
    # TODO: Save old users and put their names in old_usernames
    # TODO: Connect client to relay server and register as current server
    # TODO: Start migrator timer
    pass


# TODO: Add delayed messages from old server
# Add delayed messages from old server
@socketio.on('delayed_messages')
def update_messages():
    # TODO: Add delayed messages
    pass

# *******************************************************************


# Run chat server
if __name__ == '__main__':
    server_n = abs(int(sys.argv[1][1:]))
    server_port = sys.argv[2]
    server_type = sys.argv[3]
    sv = Server(get_local_ip(), server_port, socketio, sio_client,
                start=server_type != 'new')
    sv.N_CLIENTS_REQUIRED = server_n
    if server_type == 'new':
        old_server = sys.argv[4]
        old_server_uri = f'http://{old_server}'
        sio_client.connect(old_server_uri)
        new_server = f'http://{sv.ip}:{sv.port}'
        sio_client.emit('migrate', new_server)
    try:
        socketio.run(app, host='0.0.0.0', port=server_port)
    except KeyboardInterrupt:
        exit()
