from __init__ import create_app, socketio

# App instance
app = create_app()

# Run server
if __name__ == '__main__':
    socketio.run(app)
