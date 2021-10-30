import import_fixer

import_fixer.fix_imports()

import sys
import os
import logging
import subprocess
from flask import Flask, request
from flask_socketio import SocketIO
from functools import reduce
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
CURRENT_SERVER = 0
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


# Get numeric value from IP
def get_value(ip):
    return int(reduce(lambda i, j: i + j, [f'{int(sub):03d}' for sub in ip]))


# Get distance between IPs
def get_ip_diff(ip1, ip2) -> int:
    return abs(get_value(ip1.split('.')) - get_value(ip2.split('.')))


# Find closest chat server
def get_closest_server(client, servers):
    closest = float('inf')
    best_server = []
    for s in servers:
        distance = get_ip_diff(client[0], s[0])
        if distance < closest:
            best_server = s
            closest = distance
        elif (distance == closest) and \
                (abs(s[1] - client[1]) < abs(best_server[1] - client[1])):
            best_server = s
            closest = distance
    return best_server


# Debug replication servers
def get_different_server(client, servers):
    global CURRENT_SERVER
    chosen = CURRENT_SERVER
    if CURRENT_SERVER:
        CURRENT_SERVER = 0
    else:
        CURRENT_SERVER = 1
    return servers[chosen]


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
def connect(data):
    migration_lock.acquire()
    # Use get_different_server for debugging replication
    # TODO: chosen_server = get_closest_server(data, SERVER)
    chosen_server = get_different_server(data, SERVER)
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

        # TODO: NOTE: Change stdout from 'subprocess.DEVNULL' to 'None' for debugging
        twin = ''
        if n:
            twin = f'http://{SERVER[0][0]}:{SERVER[0][1]}'
        subprocess.Popen(['python3', f'{current_dir}/chat_server.py',
                          f'-{N_CLIENTS_REQUIRED}',
                          f'{chat_server_port}', 'original', twin],
                         stdout=None, stderr=None)
        SERVER.append([server_ip, chat_server_port])
    show_server_locations()

    # Run
    print(f'Relay Server URI: http://{server_ip}:{relay_server_port}')
    print(f'Chat Server initialized (N = {N_CLIENTS_REQUIRED})')
    try:
        socketio.run(app, host='0.0.0.0', port=relay_server_port)
    except KeyboardInterrupt:
        exit()
