import sys
import logging
from socket import socket, AF_INET, SOCK_DGRAM
from flask import Flask, request
from flask_socketio import SocketIO


# Relay server
app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.disabled = True
socketio = SocketIO(app)

# Global params
N_CLIENTS_REQUIRED = 2
SERVER = ()


# Input error handling
def notify_input_error():
    print('Invalid parameters!')
    print('   Try with:')
    print('       python3 main.py -[n]')
    print('   Where [n] is a positive integer.')


# Get local ip of the server
def get_local_ip():
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


# ************************** Socket Events **************************

# Register server
@socketio.on('register')
def register(data):
    # TODO: Register current server
    # socketio.emit('connect', SERVER, room=request.sid)
    return


# Listen for clients
@socketio.on('connect')
def connect(data):
    # TODO: Tell clients to connect to real server
    # socketio.emit('connect', SERVER, room=request.sid)
    return

# *******************************************************************


# Run relay server
if __name__ == '__main__':
    if len(sys.argv) > 1:
        try:
            N_CLIENTS_REQUIRED = abs(int(sys.argv[1][1:]))
        except ValueError:
            notify_input_error()
            exit()
    server_ip = get_local_ip()
    server_port = 5000
    # TODO: Spawn original server and register it
    print(f'LAN Server URI: http://{server_ip}:{server_port}')
    print(f'Server initialized (N = {N_CLIENTS_REQUIRED})')
    try:
        socketio.run(app, host='0.0.0.0', port=server_port)
    except KeyboardInterrupt:
        exit()
