import import_fixer

import_fixer.fix_imports()

import logging
import socketio as socketio_client
import sys
import builtins
from flask import Flask, request
from flask_socketio import SocketIO
from server import Server, get_local_ip
from signal import signal, SIGINT
from socketio import exceptions as exc
from time import sleep


# Server
app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.disabled = True
socketio = SocketIO(app)
sio_client = socketio_client.Client(handle_sigint=False)
rel_client = socketio_client.Client(handle_sigint=False)
twin_client = socketio_client.Client(handle_sigint=False)


# SIGINT handler
def safe_close(sig, frame):
    # Bypass client SIGINT
    if sv.server_type == 'new':
        return

    # Closed Relay Server (terminate all)
    sv.twin_client.disconnect()
    sleep(2)
    sv.sio.stop()
    exit()


signal(SIGINT, safe_close)


# Write server feedback on '.logs' file
def fprint(text):
    with open('.logs', 'a') as logfile:
        print(text, file=logfile)


# Broadcast queued messages
def broadcast_past_messages(sid=None):
    if sid is not None:  # Send messages to specific client
        history = []
        private_msg = sv.private[sv[sid]]
        private_idx = 0
        current_idx = 0
        for idx, msg in enumerate(sv.messages):
            if private_idx < len(private_msg):
                current_idx = private_msg[private_idx][1]
                while current_idx == idx:
                    history.append(private_msg[private_idx][0])
                    private_idx += 1
                    if private_idx < len(private_msg):
                        current_idx = private_msg[private_idx][1]
                    else:
                        current_idx = -1
            history.append(msg)
        if private_idx < len(private_msg):
            history += [x[0] for x in private_msg[private_idx:]]
        socketio.emit('msg_queue', history, room=sid)
    else:  # Send messages to everyone
        socketio.emit('msg_queue', sv.messages, broadcast=True)


# Obtain ip/port/id for private messaging and tell client to use p2p
def private(username_target, username_sender, message):
    # Store private messages
    format_msg = f'(PRIVATE) ({username_sender}) -> ' \
                 f'({username_target}): {message}'
    sv.private[username_target].append((format_msg, len(sv.messages)))

    # Replicate private messages
    try:
        if sv.twin_uri:
            sv.twin_client.emit('rep_private', {
                'target': username_target,
                'msg': (format_msg, len(sv.messages))})
    except exc.BadNamespaceError:
        pass

    # Send private message
    connection_data = sv.get_user_connections(username_target)
    if not connection_data:
        socketio.emit('show_private_msg', {
            'sender': username_sender, 'target': username_target},
                      room=request.sid)
        return
    ip, port, node_id = connection_data
    socketio.emit('send_private_msg', {
        'ip': ip, 'port': port, 'id': node_id,
        'sender': username_sender, 'target': username_target}, room=request.sid)


# Revert server to initial state
def reset_server(new_n):
    print(f'Resetting server with N = {new_n} users required')
    socketio.emit('exit', broadcast=True)
    sv.set_params(n_clients=new_n)


# Parse & delegate different commands
def command_handler(data):
    msg = data[0]
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
        if username not in (set(sv.private.keys()) - set(sv[request.sid])):
            res = 'Invalid username for private message!'
            socketio.emit('event', res, room=request.sid)
            return True
        private(username, sv[request.sid], data[1])
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
    # Service not available
    if sv.server_type == 'backup':
        return

    # Parse message
    if not command_handler(data):
        # Normal message: "USERNAME: MESSAGE"
        message = f'{sv[request.sid]}: {data[0]}'
        sv.messages_lock.acquire()
        sv.messages.append(message)
        sv.messages_lock.release()

        # Replicate message
        try:
            if sv.twin_uri:
                sv.twin_client.emit('rep_message', message)
        except exc.BadNamespaceError:
            pass

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
        return

    # Check new users
    user = data['user']

    # Invalid username
    if (not user) or (':' in user) or (' ' in user):
        socketio.emit('denied', 'Invalid username!', room=request.sid)
        return

    # New user
    if user not in sv.usernames:
        # Replicate new user
        try:
            if sv.twin_uri:
                sv.twin_client.emit('rep_new_user', data)
        except exc.BadNamespaceError:
            pass

        # Build new user
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

        # Replicate disconnection
        try:
            if sv.twin_uri:
                sv.twin_client.emit('rep_disconnect', username)
        except exc.BadNamespaceError:
            pass

        # Remove user
        sv.n_clients -= 1
        sv.usernames.remove(username)
        msg = f'{username} has left the chat!'
        sv.messages_lock.acquire()
        sv.messages.append(msg)
        sv.messages_lock.release()
        if sv.server_type == 'backup':
            return
        socketio.emit(
            'users', sv.n_clients, broadcast=True, include_self=False)
        if sv.n_clients > sv.N_CLIENTS_REQUIRED:
            socketio.emit('response', msg)


# Migrate to new server
@socketio.on('migrate')
def migrate(data):
    sv.migrator.migrate_data(data, request.sid)


# Prepare new server
@sio_client.on('prepare')
def prepare(data):
    sv.old_users = data['users']
    sv.usernames = set(data['usernames'])
    sv.rep_users = data['rep_users']
    sv.n_clients = len(sv.rep_users)
    sv.messages_lock.acquire()
    sv.messages = data['messages']
    sv.messages_lock.release()
    sv.private = data['private']
    sv.client.emit('ready')
    try:
        sv.relay_client.emit('register', {
            'new': [sv.ip, sv.port], 'old': sv.old_server[7:].split(':')})
    except exc.BadNamespaceError:
        pass
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
    if sv.old_server:
        sv.relay_client.disconnect()
    sv.twin_client.disconnect()
    sv.sio.emit('reconnect', sv.new_server)
    sv.sio.stop()


# Twin server has changed
@socketio.on('twin')
def update_twin(data):
    if sv.twin_uri == data:
        sv.can_migrate = True
        return
    if sv.twin_uri:
        sv.twin_client.disconnect()
        sleep(2)
    sv.twin_uri = data
    try:
        sv.twin_client.connect(sv.twin_uri)
        sv.can_migrate = True
    except exc.ConnectionError:
        pass


# Replicate messages
@socketio.on('rep_message')
def replicate_message(message):
    sv.messages_lock.acquire()
    sv.messages.append(message)
    sv.messages_lock.release()

    # Broadcast message
    if sv.n_clients >= sv.N_CLIENTS_REQUIRED:
        socketio.emit('response', message, broadcast=True)


# Replicate private messages
@socketio.on('rep_private')
def replicate_private(data):
    sv.private[data['target']].append(data['msg'])


# Replicate new users
@socketio.on('rep_new_user')
def replicate_new_user(data):
    sv.n_clients += 1
    sv.rep_users[data['user']] = (data['ip'], data['port'], data['id'])
    sv.usernames.add(data['user'])
    if data['user'] not in sv.private:
        sv.private[data['user']] = []
    socketio.emit('users', sv.n_clients, broadcast=True)

    # Check if N required clients have joined
    join_msg = f'{data["user"]} has joined the chat!'
    sv.messages_lock.acquire()
    sv.messages.append(join_msg)
    sv.messages_lock.release()
    if sv.n_clients == sv.N_CLIENTS_REQUIRED:
        print('Chat is now active!')
        broadcast_past_messages()
        sv.N_CLIENTS_REQUIRED = -1  # Chat is permanent from now on
    elif sv.n_clients > sv.N_CLIENTS_REQUIRED:
        socketio.emit('response', join_msg, broadcast=True)


# Replicate new users
@socketio.on('rep_disconnect')
def replicate_disconnection(username):
    # Remove user
    sv.rep_users.pop(username, False)
    sv.n_clients -= 1
    sv.usernames.remove(username)
    socketio.emit('users', sv.n_clients, broadcast=True)
    msg = f'{username} has left the chat!'
    if sv.n_clients > sv.N_CLIENTS_REQUIRED:
        socketio.emit('response', msg)
    sv.messages_lock.acquire()
    sv.messages.append(msg)
    sv.messages_lock.release()


# Shut down server
@socketio.on('shutdown')
def shutdown(data):
    sv.shutdown = True
    sv.can_migrate = False

    # Move clients to twin
    if data == 'twin':
        users_info = {f'{x.ip}:{x.port}': x.username for x in sv.users.values()}
        sv.twin_client.emit('twin_off', users_info)
        sleep(1)
        sv.sio.emit('reconnect', sv.twin_uri)
        sv.twin_client.disconnect()
        sleep(2)
        sv.sio.stop()
        return

    # Move clients to relay until new servers start
    try:
        if sv.server_type in ('original', 'new_twin'):
            sv.relay_client.connect(sv.relay)
        sv.relay_client.emit('create_server', f'http://{sv.ip}:{sv.port}')
    except (exc.ConnectionError, exc.BadNamespaceError):
        pass


# Receive twin data before twin shutdown
@socketio.on('twin_off')
def receive_twin_data(data):
    for location, username in data.items():
        sv.old_users[location] = username
    sv.rep_users = dict()
    sv.n_clients = len(sv.users)
    sv.twin_client.disconnect()
    sv.twin_uri = ''
    sv.can_migrate = True


# Sync with new twin
@socketio.on('sync')
def sync_twin(data):
    # Already migrating
    if sv.attempting:
        sv.twin_uri = data
        return

    # Sync with twin
    sv.can_migrate = False
    sv.twin_uri = data
    sv.twin_client.connect(sv.twin_uri)
    rep_users = dict()
    for user in sv.users.values():
        rep_users[user.username] = user.get_connections()
    rep_data = {'messages': sv.messages,
                'private': sv.private,
                'rep_users': rep_users,
                'twin': f'http://{sv.ip}:{sv.port}',
                'n_clients': sv.N_CLIENTS_REQUIRED}
    sv.twin_client.emit('twin_start', rep_data)


# Initialize new twin
@socketio.on('twin_start')
def initialize_twin(data):
    sv.messages_lock.acquire()
    sv.messages = data['messages']
    sv.messages_lock.release()
    sv.private = data['private']
    sv.rep_users = data['rep_users']
    sv.usernames = set(sv.rep_users.keys())
    sv.N_CLIENTS_REQUIRED = data['n_clients']
    sv.n_clients = len(sv.rep_users)
    sv.twin_uri = data['twin']
    try:
        sv.twin_client.connect(sv.twin_uri)
        sv.can_migrate = True
    except exc.ConnectionError:
        pass


# Backup data before and then shutdown
@socketio.on('backup_ready')
def backup_ready(data):
    users_info = {f'{x.ip}:{x.port}': x.username for x in sv.users.values()}
    backup_data = {'messages': sv.messages,
                   'private': sv.private,
                   'users': users_info,
                   'n_clients': sv.N_CLIENTS_REQUIRED}
    try:
        sv.twin_client.connect(data)
        sv.twin_client.emit('backup', backup_data)
        sleep(1)
    except (exc.ConnectionError, exc.BadNamespaceError):
        pass
    sv.twin_client.disconnect()
    sv.sio.emit('reconnect', data)
    sv.sio.stop()


# Prepare backup server
@socketio.on('backup')
def backup(data):
    for location, username in data['users'].items():
        sv.old_users[location] = username
    sv.rep_users = dict()
    sv.n_clients = 0
    sv.messages = data['messages']
    sv.private = data['private']
    sv.N_CLIENTS_REQUIRED = data['n_clients']

# *******************************************************************


# Run chat server
if __name__ == '__main__':
    server_n = int(sys.argv[1][1:])
    server_port = sys.argv[2]
    server_type = sys.argv[3]
    local_ip = get_local_ip()
    if server_type in ('original', 'new_twin', 'backup'):
        relay = f'http://{local_ip}:{5000}'
    else:
        relay = sys.argv[6]
    twin = sys.argv[4]
    sv = Server(local_ip, server_port, socketio, sio_client, rel_client, relay,
                twin_client, twin, server_type)
    sv.N_CLIENTS_REQUIRED = server_n

    # Mod print to add server name
    def print(*args, **kwargs):
        builtins.print(f'||| {sv.ip}:{sv.port} |||', *args, **kwargs)

    # Twin servers
    try:
        if sv.twin_uri:
            sv.twin_client.connect(sv.twin_uri)
            sv.twin_client.emit('twin', f'http://{sv.ip}:{sv.port}')
        elif sv.server_type not in ('new_twin', 'backup'):
            sv.can_migrate = True
    except (exc.ConnectionError, exc.BadNamespaceError):
        pass

    # New server setup
    if server_type not in ('original', 'new_twin', 'backup'):
        try:
            sv.relay_client.connect(sv.relay)
        except exc.ConnectionError:
            pass
        old_server = sys.argv[5]
        old_server_uri = f'http://{old_server}'
        sv.old_server = old_server_uri
        sv.client.connect(old_server_uri)
        new_server = f'http://{sv.ip}:{sv.port}'
        sv.client.emit('migrate', new_server)
    try:
        socketio.run(app, host='0.0.0.0', port=server_port)
    finally:
        exit()
