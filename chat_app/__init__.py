import sys
from flask import Flask, request
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_migrate import Migrate


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
        self.set_params()

    def set_params(self, N_CLIENTS_REQUIRED=2):
        # Client counter
        self.N_CLIENTS_REQUIRED = N_CLIENTS_REQUIRED
        self.clients = 0

        # Users
        self.users = dict()  # Key: socket ID, Value: Username
        self.user_data = dict()  # Key: Username, Value: IP/Port

        # Usernames set (for quickly checking existence)
        self.usernames = set()

        # Messages
        self.messages = []


gb = GlobalParams()


# Broadcast queued messages
def broadcast_past_messages(sid=None):
    if sid is not None:  # Send messages to specific client
        socketio.emit('msg_queue', gb.messages, room=sid)
    else:  # Send messages to everyone
        socketio.emit('msg_queue', gb.messages, broadcast=True)


def command_handler(msg):
    # $reset -n --> reinicia usuarios, mensajes y N necesario.
    if "$reset" in msg:
        try:
            msg = msg.strip().split(" ")
            new_N = int(msg[1][1:])
            reset_server(new_N)
        except (IndexError, ValueError):
            print("Comando no cumple formato: $reset -N")
    else:
        print("Comando no encontrado")


def reset_server(new_N):
    print(f"Resetting server with N={new_N} users required.")
    gb.set_params(N_CLIENTS_REQUIRED=new_N)
    socketio.emit('graceful_disconnect', broadcast=True)
    # socketio.run(create_app())

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

        message = f'{gb.users[request.sid]}: {msg}'
        if msg[0] == "$":
            command_handler(msg)
        else:
            gb.messages.append(message)

        # Broadcast message
        if gb.clients >= N_CLIENTS_REQUIRED:
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
            gb.user_data[user] = (
                data['ip'], data['port'], data['id'])
            socketio.emit('users_add', {
                'count': gb.clients, 'users': list(gb.usernames)}, room=request.sid)
            gb.usernames.add(user)
            socketio.emit('users_add', {
                'count': gb.clients, 'users': [user]},
                          broadcast=True, include_self=False)
            socketio.emit('accepted', room=request.sid)
        else:  # Login failed
            socketio.emit('denied', f'{user} is already in use!',
                          room=request.sid)
            return

        # Check if N required clients have joined
        join_msg = f'{user} has joined the chat!'
        gb.messages.append(join_msg)
        if gb.clients == gb.N_CLIENTS_REQUIRED:
            broadcast_past_messages()
            gb.N_CLIENTS_REQUIRED = -1  # Chat is permanent from now on
        elif gb.clients > gb.N_CLIENTS_REQUIRED:
            broadcast_past_messages(request.sid)
            socketio.emit('response', join_msg, broadcast=True,
                          include_self=False)

    # User disconnects
    @socketio.on('disconnect')
    def disconnect():
        global clients
        username = gb.users.pop(request.sid, False)
        if username:
            gb.clients -= 1
            gb.usernames.remove(username)
            socketio.emit('users_remove', {
                'count': gb.clients, 'user': username},
                          broadcast=True, include_self=False)
            msg = f'{username} has left the chat!'
            if gb.clients > N_CLIENTS_REQUIRED:
                socketio.emit('response', msg)
                gb.messages.append(msg)
            else:
                gb.messages.append(msg)

    @socketio.on('private')
    def private(username):
        ip, port, node_id = gb.user_data[username]
        socketio.emit('send_private_msg', {
            'ip': ip, 'port': port, 'id': node_id,
            'origin': gb.users[request.sid]}, room=request.sid)

    return app


# Input error handling
def notify_input_error():
    print("🚨 Invalid parameters!")
    print("   Try with:")
    print("       python __init__.py -[n]")
    print("   Where [n] is a positive integer.")


# Run server
if __name__ == '__main__':
    if len(sys.argv) > 1:
        try:
            N_CLIENTS_REQUIRED = abs(int(sys.argv[1][1:]))
        except ValueError:
            notify_input_error()
            exit()
        print(f'⏳ Waiting for {N_CLIENTS_REQUIRED} clients to join...')
        # TODO: It would be ideal print the server address (ip:port)
        socketio.run(create_app())
