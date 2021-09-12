from . import create_app, socketio

# App instance
chat_app = create_app()

# Run server
if __name__ == '__main__':
    socketio.run(chat_app)
