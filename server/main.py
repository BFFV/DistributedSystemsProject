import logging
import os
import subprocess
import sys
from flask import Flask, request
from flask_socketio import SocketIO
from server import get_local_ip, get_free_port


# Relay server
app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.disabled = True
socketio = SocketIO(app)

# Global params
N_CLIENTS_REQUIRED = 2
SERVER = []
MIGRATING = False


# Input error handling
def notify_input_error():
    print('Invalid parameters!')
    print('   Try with:')
    print('       python3 main.py -[n]')
    print('   Where [n] is a positive integer.')


# ************************** Socket Events **************************

# Register server
@socketio.on('register')
def register(data):
    global SERVER, MIGRATING
    SERVER = data
    MIGRATING = False


# Currently in a migration
@socketio.on('migrating')
def migrating():
    global MIGRATING
    MIGRATING = True


# Listen for clients
@socketio.on('connect_to_chat')
def connect():
    while MIGRATING:
        pass
    socketio.emit('connect_to_chat', SERVER, room=request.sid)

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
    relay_server_port = 5000

    # Run first chat server
    chat_server_port = get_free_port()
    current_dir = os.path.dirname(os.path.realpath(__file__))

    # NOTE: Change stdout from 'subprocess.DEVNULL' to 'None' for debugging
    subprocess.Popen(['python3', f'{current_dir}/chat_server.py',
                      f'-{N_CLIENTS_REQUIRED}',
                      f'{chat_server_port}', 'original'],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    SERVER = [server_ip, chat_server_port]

    # Run
    print(f'LAN Server URI: http://{server_ip}:{relay_server_port}')
    print(f'Server initialized (N = {N_CLIENTS_REQUIRED})')
    try:
        socketio.run(app, host='0.0.0.0', port=relay_server_port)
    except KeyboardInterrupt:
        exit()
