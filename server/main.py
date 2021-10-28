import logging
import os
import random
import subprocess
import sys
from flask import Flask, request
from flask_socketio import SocketIO
from server import get_local_ip, get_free_port
from threading import Lock


# Relay server
app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.disabled = True
socketio = SocketIO(app)

# Global params
N_CLIENTS_REQUIRED = 2
SERVER = []
migration_lock = Lock()


# Input error handling
def notify_input_error():
    print('Invalid parameters!')
    print('   Try with:')
    print('       python3 main.py -[n]')
    print('   Where [n] is a positive integer.')


# Show current chat servers
def show_server_locations():
    print('\n**Current Chat Servers**\n')
    for s in SERVER:
        print(f'Chat: {s[0]}:{s[1]}')
    print()


# ************************** Socket Events **************************

# Register server
@socketio.on('register')
def register(data):
    global SERVER
    migration_lock.acquire()
    current_server = 0
    for idx, s in enumerate(SERVER):
        if (s[0] == data['old'][0]) and (s[1] == int(data['old'][1])):
            current_server = idx
    SERVER[current_server] = [data['new'][0], int(data['new'][1])]
    show_server_locations()
    migration_lock.release()


# Listen for clients
@socketio.on('connect_to_chat')
def connect():
    migration_lock.acquire()
    # TODO: Choose closest server to client
    chosen_server = random.choice(SERVER)
    socketio.emit('connect_to_chat', chosen_server, room=request.sid)
    migration_lock.release()

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

    # Run initial chat servers
    current_dir = os.path.dirname(os.path.realpath(__file__))
    for n in range(2):
        chat_server_port = get_free_port()

        # NOTE: Change stdout from 'subprocess.DEVNULL' to 'None' for debugging
        # TODO: creationflags=subprocess.CREATE_NEW_CONSOLE (windows only)
        subprocess.Popen(['python3', f'{current_dir}/chat_server.py',
                          f'-{N_CLIENTS_REQUIRED}',
                          f'{chat_server_port}', 'original'],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        SERVER.append([server_ip, chat_server_port])
    show_server_locations()

    # Run
    print(f'Relay Server URI: http://{server_ip}:{relay_server_port}')
    print(f'Chat Server initialized (N = {N_CLIENTS_REQUIRED})')
    try:
        socketio.run(app, host='0.0.0.0', port=relay_server_port)
    except KeyboardInterrupt:
        exit()
