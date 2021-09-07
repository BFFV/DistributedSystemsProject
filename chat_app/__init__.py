import sys
from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_migrate import Migrate
from dataclasses import dataclass, field
if sys.argv[-1] == 'run':                    # Si se ejecuta 'flask run'
    from .models import db, Message
else:                                       # Si se ejecuta 'python3 __init__.py -n'
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
# Lista de mensajes (Message) que recibió el servidor
messages = []

@dataclass
class User:
    username: str
    id_: int
    # lista de instancias Message
    messages: list = field(default_factory=list)

def craft_response_message(message):
    return {
        "user": message.sent_by, 
        "text": message.text
    }

def broadcast_past_messages():
    global messages

    for message in messages:
        # response = f'{message.sent_by}: {message.text}'
        response = craft_response_message(message)
        socketio.emit('response', response, broadcast=True)

    messages = []

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
            # Solución barata, así una vez conectados todos el N no afecta.
            N_CLIENTS_REQUIRED = 0
        else:
            pass

    @socketio.on('disconnect', namespace="/")
    def disconnect():
        global clients, messages
        clients -= 1
        socketio.emit("users", {"user_count": clients}, broadcast=True)
        if clients == 0:
            messages = []

    @socketio.on('message')
    def handle_message(json):
        print('received message: ' + str(json))
        message = Message(json["text"], json["user"])
        # TODO: insertar mensaje en usuario correcto de lista users

        # Esto guarda el mensaje en PostgreSQL:
        # Message.insert(message)
        if clients >= N_CLIENTS_REQUIRED:
            # response = f'{json["user"]}: {json["text"]}'
            response = craft_response_message(message)
            socketio.emit('response', response, broadcast=True)
        else:
            messages.append(message)

    @socketio.on('login')
    def handle_login(json):
        print('received login ' + str(json))
        response = f'{json["userKey"]} just enter the Server'
        socketio.emit('response', response)

    return app


def notify_input_error():
    print("🚨 Parámetros ingresados de forma incorrecta. Intenta nuevamente.")
    print("   Prueba con la forma:")
    print("       python __init__.py -[N]")
    print("   Donde [N] corresponde a un número entero positivo.")




if __name__ == '__main__':

    if len(sys.argv) != 2:
        notify_input_error()
        exit()
    elif len(sys.argv) == 2:
        try:
            N_CLIENTS_REQUIRED = abs(int(sys.argv[-1][1:]))
        except ValueError:
            notify_input_error()
            exit()
        print(f"⏳ Esperando a que se conecten {N_CLIENTS_REQUIRED} clientes...")

    socketio.run(create_app())
    