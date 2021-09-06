from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_migrate import Migrate
from .models import db, Message


migrate = Migrate()
socketio = SocketIO()

# Env vars
db_user = 'postgres'
db_password = 'postgres'
db_url = 'localhost:5432'
db_name = 'chat_db'

global clients

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
        # global variable as it needs to be shared
        # print(json['data'])
        print("entre aca")
        global clients
        clients += 1
        print(clients)
        # emits a message with the user count anytime someone connects
        socketio.emit("users", {"user_count": clients}, broadcast=True)

    @socketio.on('disconnect', namespace="/disconnect")
    def disconnect():
        global clients
        clients -= 1
        socketio.emit("users", {"user_count": clients}, broadcast=True)
        
    @socketio.on('message')
    def handle_message(json):
        print('received message: ' + str(json))
        #message = Message(json["message"], json["user_name"])
        #Message.insert(message)
        response = f'{json["user"]}: {json["text"]}'
        socketio.emit('response', response)

    @socketio.on('login')
    def handle_login(json):
        print('received login ' + str(json))
        response = f'{json["userKey"]} just enter the Server'
        socketio.emit('response', response)

    return app

#if __name__ == '__main__':
#    socketio.run(create_app())