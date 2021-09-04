import socketio

# Socket IO client
sio = socketio.Client()

@sio.event
def connect():
    pass
    #sio.emit('login', {'userKey': 'streaming_api_key'})
    #sio.emit('message', {'data': 'User Connected'})

@sio.event
def connect_error():
    print("The connection failed!")

@sio.event
def message(data):
    print('I received a message!')

@sio.on('response')
def on_message(data):
    print('\n' + data + '\n')


# Run client
if __name__ == '__main__':
    sio.connect('http://127.0.0.1:5000')
    try:
        while True:
            message = input()
            sio.emit('message', {'text': message, 'user': 'Benja'})
    except KeyboardInterrupt:
        sio.disconnect()
