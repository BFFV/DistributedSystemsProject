import socketio
import re

# Socket IO client
sio = socketio.Client()

@sio.event
def connect():
    sio.emit('connect', {'data': 'trying to connect'})
    

@sio.event
def login(username):
    sio.emit('login', {'userKey': 'streaming_api_key'})
    sio.emit('message', {'data': 'User Connected'})

@sio.event
def connect_error():
    print("The connection failed!")

@sio.event
def message(data):
    print('I received a message!')

@sio.on('response')
def on_message(data):
    print('\n' + data + '\n')

@sio.on('users')
def on_message(data):
    print('\n' + data + '\n')


# Run client
if __name__ == '__main__':
    # try:
    #     sio.connect('http://127.0.0.1:5000')
    # except TypeError:
    #     print("No se logro conectar al servidor")
    # username = "user name"
    # while not re.match("^[a-zA-Z0-9_.-]+$", username):
    #     username = input("Ingrese su nombre de usuario: ")
    #     if not re.match("^[a-zA-Z0-9_.-]+$", username):
    #         print("Ingrese caracteres alfanumericos o _.-")
    sio.connect('http://127.0.0.1:5000')
    try:
        while True:
            message = input()
            sio.emit('message', {'text': message, 'user': 'Benja'})
    except KeyboardInterrupt:
        sio.disconnect()
