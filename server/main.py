import sys
import logging
from socket import socket, AF_INET, SOCK_DGRAM
from flask import Flask, request
from flask_socketio import SocketIO


# Server
app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.disabled = True
socketio = SocketIO(app)


# Global parameters
class GlobalParams:
    def __init__(self) -> None:
        # Client counter
        self.N_CLIENTS_REQUIRED = 2
        self.clients = 0

        # Users
        self.users = dict()  # Key: socket ID, Value: Username
        self.user_data = dict()  # Key: Username, Value: IP/Port

        # Usernames set (for quickly checking existence)
        self.usernames = set()

        # Messages
        self.messages = []

    def set_params(self, n_clients=2):
        self.N_CLIENTS_REQUIRED = n_clients
        self.clients = 0
        self.users = dict()
        self.user_data = dict()
        self.usernames = set()
        self.messages = []
        print(f'Server initialized (N = {self.N_CLIENTS_REQUIRED})')


gb = GlobalParams()


# Broadcast queued messages
def broadcast_past_messages(sid=None):
    if sid is not None:  # Send messages to specific client
        socketio.emit('msg_queue', gb.messages, room=sid)
    else:  # Send messages to everyone
        socketio.emit('msg_queue', gb.messages, broadcast=True)


# Obtain ip/port/id for private messaging
def private(username):
    ip, port, node_id = gb.user_data[username]
    socketio.emit('send_private_msg', {
        'ip': ip, 'port': port, 'id': node_id,
        'origin': gb.users[request.sid]}, room=request.sid)


# Revert server to initial state
def reset_server(new_n):
    print(f'Resetting server with N = {new_n} users required')
    socketio.emit('exit', broadcast=True)
    gb.set_params(n_clients=new_n)


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
        if username not in (gb.usernames - set(gb.users[request.sid])):
            res = 'Invalid username for private message!'
            socketio.emit('event', res, room=request.sid)
            return True
        private(username)
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


# Input error handling
def notify_input_error():
    print('Invalid parameters!')
    print('   Try with:')
    print('       python3 main.py -[n]')
    print('   Where [n] is a positive integer.')


# Get local ip of the server
def get_local_ip():
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


# ************************** Socket Events **************************

# Listen for messages
@socketio.on('message')
def handle_message(data):
    # Parse message
    if not command_handler(data):
        # Normal message
        message = f'{gb.users[request.sid]}: {data}'
        gb.messages.append(message)

        # Broadcast message
        if gb.clients >= gb.N_CLIENTS_REQUIRED:
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
    if user not in gb.usernames:
        gb.clients += 1
        gb.users[request.sid] = user
        gb.user_data[user] = (data['ip'], data['port'], data['id'])
        gb.usernames.add(user)
        socketio.emit('users', gb.clients, broadcast=True)
        socketio.emit('accepted', room=request.sid)
    else:  # Login failed
        socketio.emit('denied', f'{user} is already in use!', room=request.sid)
        return

    # Check if N required clients have joined
    join_msg = f'{user} has joined the chat!'
    gb.messages.append(join_msg)
    if gb.clients == gb.N_CLIENTS_REQUIRED:
        print('Chat is now active!')
        broadcast_past_messages()
        gb.N_CLIENTS_REQUIRED = -1  # Chat is permanent from now on
    elif gb.clients > gb.N_CLIENTS_REQUIRED:
        broadcast_past_messages(request.sid)
        socketio.emit('response', join_msg, broadcast=True,
                      include_self=False)


# User disconnects
@socketio.on('disconnect')
def disconnect():
    username = gb.users.pop(request.sid, False)
    if username:
        gb.clients -= 1
        gb.usernames.remove(username)
        socketio.emit(
            'users', gb.clients, broadcast=True, include_self=False)
        msg = f'{username} has left the chat!'
        if gb.clients > gb.N_CLIENTS_REQUIRED:
            socketio.emit('response', msg)
        gb.messages.append(msg)

# *******************************************************************


# Run server
if __name__ == '__main__':
    if len(sys.argv) > 1:
        try:
            gb.N_CLIENTS_REQUIRED = abs(int(sys.argv[1][1:]))
        except ValueError:
            notify_input_error()
            exit()
    server_ip = get_local_ip()
    server_port = 5000
    print(f'LAN Server URI: http://{server_ip}:{server_port}')
    print(f'Server initialized (N = {gb.N_CLIENTS_REQUIRED})')
    print(f'Waiting for {gb.N_CLIENTS_REQUIRED} clients to join...')
    try:
        socketio.run(app, host='0.0.0.0', port=server_port)
    except KeyboardInterrupt:
        exit()
