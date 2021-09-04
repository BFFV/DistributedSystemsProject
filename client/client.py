import socketio

# standard Python
sio = socketio.Client()

@sio.event
def connect():
    print("I'm connected!")
    #sio.emit('login', {'userKey': 'streaming_api_key'})
    #sio.emit('message', {'data': 'User Connected'})

@sio.event
def connect_error():
    print("The connection failed!")

@sio.event
def message(data):
    print('I received a message!')

@sio.on('handshake')
def on_message(data):
    print('HandShake', data)
    sio.emit('symbolSub', {'symbol': 'USDJPY'})
    sio.emit('symbolSub', {'symbol': 'GBPUSD'})
    sio.emit('symbolSub', {'symbol': 'EURUSD'})

@sio.on('price')
def on_message(data):
    print('Price Data ', data)


sio.connect('http://localhost:5000')
print('my sid is', sio.sid)
