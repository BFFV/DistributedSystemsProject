from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_migrate import Migrate


migrate = Migrate()
socketio = SocketIO()


def create_app():
    # create and configure the app
    app = Flask(__name__)

    # Database configuration
    database_name = 'chat_distribuidos'
    default_database_path = "postgresql://{}:{}@{}/{}" \
        .format('postgres', 'postgres', 'localhost:5432', database_name)
    app.config["SQLALCHEMY_DATABASE_URI"] = default_database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    socketio.init_app(app)
    from .models import db, Message
    db.init_app(app)
    migrate.init_app(app, db)

    CORS(app)

    @app.route('/')
    def sessions():
        return render_template('index.html')

    @socketio.on('my event')
    def handle_event(data):
        print('received message: ' + str(data))

    @socketio.on('message')
    def handle_message(json):
        print('received message: ' + str(json))

        message = Message(json["message"], json["user_name"])
        Message.insert(message)

        socketio.emit('my response', json)

    return app


