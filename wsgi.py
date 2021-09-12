from chat_app.__init__ import create_app, socketio

# Run server
if __name__ == '__main__':
    socketio.run(create_app())
