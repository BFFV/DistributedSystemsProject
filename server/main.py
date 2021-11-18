import import_fixer

import_fixer.fix_imports()

import sys
import os
import logging
import socketio as socketio_client
import subprocess
from flask import Flask, request
from flask_socketio import SocketIO
from functools import reduce
from server import get_local_ip, get_free_port
from threading import Lock, Thread


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

# Control state for chat servers
active_servers = 2
master_client = socketio_client.Client()
ask_input = f'{54 * "-"}\nComandos:{44 * " "}|\n{53 * " "}|\n' \
            f'"APAGAR -N" -> apaga el servidor número N' \
            f'{12 * " "}|\n' \
            f'"PRENDER -N" -> prende el servidor número N' \
            f'{10 * " "}|\n' \
            f'{54 * "-"}\n\n' \
            f'Escribir Comando:\n'


# Input error handling
def notify_input_error():
    print('Invalid parameters!')
    print('   Try with:')
    print('       python3 main.py -[n]')
    print('   Where [n] is a positive integer.')


# Show current chat servers
def show_server_locations():
    print('\n**Current Chat Servers**\n')
    for idx, s in enumerate(SERVER):
        if not s:
            print(f'Chat Server {idx + 1}: INACTIVE')
        else:
            print(f'Chat Server {idx + 1}: {s[0]}:{s[1]} (ACTIVE)')
    print()
    print(ask_input)


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
    for s in [sv for sv in servers if sv]:
        distance = get_ip_diff(client[0], s[0])
        if distance < closest:
            best_server = s
            closest = distance
        elif (distance == closest) and (s[1] < best_server[1]):
            best_server = s
            closest = distance
    if best_server:
        return best_server
    return False


# Debug replication servers
def get_different_server(client, servers):
    global CURRENT_SERVER
    chosen = CURRENT_SERVER
    if CURRENT_SERVER:
        CURRENT_SERVER = 0
    else:
        CURRENT_SERVER = 1
    return servers[chosen]


# Check manager input
def check_input(command):
    try:
        c = command.strip('\n').split()
        if len(c) != 2:
            return False, ''
        state = c[0]
        server_n = abs(int(c[1][1:]))
        if state not in ('APAGAR', 'PRENDER') or server_n not in range(1, 3):
            return False, ''
        if state == 'APAGAR':
            if not SERVER[server_n - 1]:
                return False, ''
            return server_n, 'off'
        if state == 'PRENDER':
            if SERVER[server_n - 1]:
                return False, ''
            return server_n, 'on'
    except ValueError:
        return False, ''


# TODO: Manage state of chat servers
def manage_state():
    global active_servers, SERVER
    try:
        while True:
            user_input = input()
            s_n, op = check_input(user_input)
            if s_n:
                if op == 'off':
                    s = SERVER[s_n - 1]
                    master_client.connect(f'http://{s[0]}:{s[1]}')
                    shutdown_type = 'twin'
                    if active_servers < 2:
                        shutdown_type = 'backup'
                    master_client.emit('shutdown', shutdown_type)
                    master_client.disconnect()
                    SERVER[s_n - 1] = None
                    active_servers -= 1
                else:
                    print(f'start server {s_n}')
                    # TODO: start server s
                    # call start server
                    active_servers += 1
                show_server_locations()
            else:
                print('Comando Inválido!!!\n')
            print(ask_input)
    except EOFError:
        pass


# TODO: Start chat server
def start_server():
    # Check if both are down or just one
    # Spawn new server of type new_rel, make sure it syncs with twin
    pass


# ************************** Socket Events **************************

# Register server
@socketio.on('register')
def register(data):
    global SERVER
    migration_lock.acquire()
    current_server = 0
    for idx, s in enumerate(SERVER):
        if s and (s[0] == data['old'][0]) and (s[1] == int(data['old'][1])):
            current_server = idx
    SERVER[current_server] = [data['new'][0], int(data['new'][1])]
    show_server_locations()
    migration_lock.release()


# Listen for clients
@socketio.on('connect_to_chat')
def connect(data):
    migration_lock.acquire()
    # NOTE: Use get_different_server for debugging replication
    chosen_server = get_closest_server(data, SERVER)
    # TODO: check when both servers are down
    socketio.emit('connect_to_chat', chosen_server, room=request.sid)
    migration_lock.release()


# TODO: Backup server for keeping clients connected until a server is started
@socketio.on('create_server')
def create_server(data):
    server_port = get_free_port()
    c_dir = os.path.dirname(os.path.realpath(__file__))
    n_clients = data['n_clients']
    ip = data['ip']
    port = data['port']
    rel = data['relay']
    twin_data = data['twin']

    # NOTE: Change stdout from "subprocess.DEVNULL" to "None" for debugging
    subprocess.Popen(['python3', f'{c_dir}/chat_server.py',
                      f'-{n_clients}', f'{server_port}', 'backup', twin_data,
                      f'{ip}:{port}', f'{rel}'],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

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
    print(f'Chat Servers initialized (N = {N_CLIENTS_REQUIRED})')
    controller = Thread(target=manage_state, daemon=True)
    controller.start()
    try:
        socketio.run(app, host='0.0.0.0', port=relay_server_port)
    except KeyboardInterrupt:
        exit()
