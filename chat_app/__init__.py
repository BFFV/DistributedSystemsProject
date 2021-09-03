from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_migrate import Migrate

import os


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
    from .models import db, User, Message
    db.init_app(app)
    migrate.init_app(app, db)

    CORS(app)

    @app.route('/')
    def sessions():
        return render_template('session.html')

    def message_received(methods=['GET', 'POST']):
        print('message was received!!!')

    @socketio.on('my event')
    def handle_my_custom_event(json, methods=['GET', 'POST']):
        print('received my event: ' + str(json))
        socketio.emit('my response', json, callback=message_received)

    return app


