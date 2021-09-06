import sys
from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_migrate import Migrate
from dataclasses import dataclass, field
if sys.argv[1] == 'run':
    from .models import db, Message
else:
    from models import db, Message



migrate = Migrate()
socketio = SocketIO()

# Env vars
db_user = 'postgres'
db_password = 'postgres'
db_url = 'localhost:5432'
db_name = 'chat_db'

N_CLIENTS_REQUIRED = 2
# Variable global, contador de clientes
clients = 0
# Arreglo de instancias User
users = list()
# Set de usernames, usado para rápidamente verificar si hay nombres de usuarios repetidos
usernames = set()

@dataclass
class User:
    username: str
    id_: int
    # lista de instancias Message
    messages: list = field(default_factory=list)

def broadcast_past_messages():
    pass

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

    @app.route('/')
    def sessions():
        return render_template('index.html')

    @socketio.on('connect', namespace='/')
    def connect():
        global clients, N_CLIENTS_REQUIRED
        clients += 1
        print(clients)
        # emits a message with the user count anytime someone connects
        socketio.emit("users", {"user_count": clients}, broadcast=True)
        # Lo dejaré hard-coded por el momento, se define globalmente
        if clients == N_CLIENTS_REQUIRED:
            broadcast_past_messages()
        else:
            pass

    @socketio.on('disconnect', namespace="/")
    def disconnect():
        global clients
        clients -= 1
        socketio.emit("users", {"user_count": clients}, broadcast=True)
        
    @socketio.on('message')
    def handle_message(json):
        print('received message: ' + str(json))
        message = Message(json["text"], json["user"])
        # TODO: insertar mensaje en usuario correcto de lista userspodr

        # Esto guarda el mensaje en PostgreSQL:
        # Message.insert(message)
        response = f'{json["user"]}: {json["text"]}'
        socketio.emit('response', response, broadcast=True)

    @socketio.on('login')
    def handle_login(json):
        print('received login ' + str(json))
        response = f'{json["userKey"]} just enter the Server'
        socketio.emit('response', response)

    return app




if __name__ == '__main__':
    
    # TO-DO: Arreglar con -N con N = un int
    if len(sys.argv) == 2:
        N_CLIENTS_REQUIRED = int(sys.argv[-1][1:])
    print(f"Esperando a que se conecten {N_CLIENTS_REQUIRED} clientes...")
    socketio.run(create_app())

    
    
    
    
    
    