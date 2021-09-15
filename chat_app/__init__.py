import sys
from flask import Flask, request
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_migrate import Migrate
from socket import socket, AF_INET, SOCK_DGRAM


# Command line options
if '.py' in sys.argv[0]:   # If using 'python3 __init__.py -n'
    from models import db, Message
else:                      # If using 'flask run'
    from .models import db, Message

# Sockets & migrations
migrate = Migrate()
socketio = SocketIO()

# Env vars (for future improvements in storage)
db_user = 'postgres'
db_password = 'postgres'
db_url = 'localhost:5432'
db_name = 'chat_db'


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


# Create app
def create_app():
    # Create and configure the app
    app = Flask(__name__)

    # Database configuration
    default_database_path = "postgresql://{}:{}@{}/{}" \
        .format(db_user, db_password, db_url, db_name)
    app.config['SQLALCHEMY_DATABASE_URI'] = default_database_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # App configuration
    socketio.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    # Listen for messages
    @socketio.on('message')
    def handle_message(msg):
        # Save message to PostgreSQL (maybe for future improvements):
        # message = Message(msg, users[request.sid])
        # Message.insert(message)

        # Parse message
        if not command_handler(msg):
            # Normal message
            message = f'{gb.users[request.sid]}: {msg}'
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

            # NOTE: This code obtains the client ip from the server side
            """
            client_ip = request.environ['REMOTE_ADDR']
            if request.environ.get('HTTP_X_FORWARDED_FOR'):
                client_ip = request.environ['HTTP_X_FORWARDED_FOR']
            gb.user_data[user] = (client_ip, data['port'], data['id'])
            """

            # NOTE: This code uses the ip provided by the client
            gb.user_data[user] = (data['ip'], data['port'], data['id'])
            gb.usernames.add(user)
            socketio.emit('users', gb.clients, broadcast=True)
            socketio.emit('accepted', room=request.sid)
        else:  # Login failed
            socketio.emit('denied', f'{user} is already in use!',
                          room=request.sid)
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

    return app


# Input error handling
def notify_input_error():
    print('🚨 Invalid parameters!')
    print('   Try with:')
    print('       python __init__.py -[n]')
    print('   Where [n] is a positive integer.')


# Get local ip of the server
def get_local_ip():
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


# Run server
if __name__ == '__main__':
    if len(sys.argv) > 1:
        try:
            gb.N_CLIENTS_REQUIRED = abs(int(sys.argv[1][1:]))
        except ValueError:
            notify_input_error()
            exit()
    print(f'💻 LAN Server URI: {get_local_ip()}')
    print(f'Server initialized (N = {gb.N_CLIENTS_REQUIRED})')
    print(f'⏳ Waiting for {gb.N_CLIENTS_REQUIRED} clients to join...')
    socketio.run(create_app())
