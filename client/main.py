import os
import p2p
import socketio
import subprocess
import sys
from collections import deque
from socketio import exceptions as exc
from threading import Lock


# Socket IO client
sio_a = socketio.Client()
sio_b = socketio.Client()
sio = sio_a
current_sio = 0
relay_client = socketio.Client()
connected = False
connecting = False
accepted = False
sio_lock = Lock()

# Users
count = 1  # User count

# Chat window
chat = deque()  # Messages (maxlen param for last X messages)
print_lock = Lock()  # Protect the print_state function
chat_is_active = False  # Check if chat is active (N users required)
ask_input = f'{54 * "-"}\nSpecial Commands:{36 * " "}|\n{53 * " "}|\n' \
            f'"$private USER MSG" -> send MSG to USER in private' \
            f'{3 * " "}|\n' \
            f'{54 * "-"}\n\n' \
            f'Type your message:\n'

# Private message
private_ready = True  # Protect current private message until p2p is ready
private_msg = ''  # Current private message


# Print chat & events
def print_state():
    width = os.get_terminal_size().columns
    print('\n')
    print(width * '*')
    print((width - 4) // 2 * ' ' + 'CHAT')
    print(width * '*')
    if not chat:
        print('No messages!')
    for msg in list(chat):
        print(msg)
    print('\n' + width * '*')
    print(f'Users Connected: {count}')
    print(width * '*')
    print('\n' + ask_input)


# Connection error
@sio_a.event
@sio_b.event
def connect_error(msg):
    print(f'\nError connecting to the server!\nDetails: {msg}\n')


# User login to the chat
def user_login():
    username = input('\nUsername (no spaces or ":" allowed): ')
    print('')
    sio.emit('login', {
        'user': username,
        'ip': p2p_node.host, 'port': p2p_node.port,
        'id': p2p_node.id
    })


# Disconnect
@sio_a.on('exit')
@sio_b.on('exit')
def disconnect():
    global accepted
    accepted = False


# Finish program
def graceful_disconnect():
    global accepted
    accepted = False
    print_lock.acquire()
    print('Goodbye!\n')
    print('Waiting for connections to close...')
    print_lock.release()
    sio.disconnect()
    relay_client.disconnect()
    p2p_node.stop()
    exit()


# Username is valid
@sio_a.on('accepted')
@sio_b.on('accepted')
def login_success():
    global accepted
    accepted = True


# Username is already in use
@sio_a.on('denied')
@sio_b.on('denied')
def login_failed(msg):
    print_lock.acquire()
    print(msg)
    print_lock.release()
    user_login()


# Send message to server
def send_message():
    global private_msg
    if not chat_is_active:
        print(ask_input)
    message = input()
    print('')
    msg = message.strip().split()
    if msg and msg[0] == '$exit':  # Exit program
        raise KeyboardInterrupt
    if msg and msg[0] == '$private':  # Private message
        if len(msg) >= 3:
            private_msg = ' '.join(msg[2:])
            sio_lock.acquire()
            sio.emit('message', ' '.join(msg[:2]))  # To protect private text
            sio_lock.release()
            return
    if not accepted:  # Server was reset
        print_lock.acquire()
        print('Closing client due to server reset!\n')
        print_lock.release()
        raise KeyboardInterrupt
    sio_lock.acquire()
    sio.emit('message', message)
    sio_lock.release()


# Update user count
@sio_a.on('users')
@sio_b.on('users')
def users_count(data):
    global count
    count = data


# Show messages in chat
@sio_a.on('response')
@sio_b.on('response')
def receive_message(msg):
    if accepted:
        print_lock.acquire()
        chat.append('\n' + msg)
        print_state()
        print_lock.release()


# Show event messages (usually input errors)
@sio_a.on('event')
@sio_b.on('event')
def receive_event(msg):
    if accepted:
        print_lock.acquire()
        print(msg)
        print('\n' + ask_input)
        print_lock.release()


# Show many messages in chat
@sio_a.on('msg_queue')
@sio_b.on('msg_queue')
def receive_messages(msgs):
    global chat_is_active
    chat_is_active = True
    if accepted:
        print_lock.acquire()
        for msg in msgs:
            chat.append('\n' + msg)
        print('Chat is now active!')
        print_state()
        print_lock.release()


# Send private message via p2p
@sio_a.on('send_private_msg')
@sio_b.on('send_private_msg')
def send_private_message(data):
    global private_ready
    private_ready = False
    peer = p2p.get_peer(p2p_node, data)
    if not peer and not \
            (p2p_node.host == data['ip'] and p2p_node.port == data['port']):
        p2p.connect(p2p_node, data['ip'], data['port'])
    peer = p2p.get_peer(p2p_node, data)
    if peer:
        private_message = f'(PRIVATE) ({data["sender"]}) -> ' \
                          f'({data["target"]}): {private_msg}'
        p2p_node.send_to_node(peer, private_message)
        chat.append('\n' + private_message)
        print_lock.acquire()
        print('Private message sent successfully!')
        if chat_is_active:
            print_state()
        print_lock.release()
    else:
        print_lock.acquire()
        print('Failed to send private message!')
        print('\n' + ask_input)
        print_lock.release()
    private_ready = True


# Callback function for private messaging
def private_event(event, this, other, data):
    if event == 'node_message':
        print_lock.acquire()
        chat.append('\n' + data)
        print_state()
        print_lock.release()


# Connect to real server
@relay_client.on('connect_to_chat')
def connect_to_chat(data):
    global connected, connecting
    if debug:
        print(f'\nConnecting to server: http://{data[0]}:{data[1]}\n')
    try:
        sio.connect(f'http://{data[0]}:{data[1]}')
        connected = True
        if debug:
            print('Connected successfully!\n')
    except exc.ConnectionError:
        if debug:
            print('Trying to connect again...\n')
        connected = False
    connecting = False


# Create new server from this client
@sio_a.on('create_server')
@sio_b.on('create_server')
def create_server(data):
    server_port = p2p.get_free_port()
    current_dir = os.path.dirname(os.path.realpath(__file__))
    n_clients = data['n_clients']
    ip = data['ip']
    port = data['port']
    rel = data['relay']
    if debug:
        print('Creating new server...\n')

    # NOTE: Change stdout from "subprocess.DEVNULL" to "None" for debugging
    subprocess.Popen(['python3', f'{current_dir}/../server/chat_server.py',
                      f'-{n_clients}', f'{server_port}', 'new',
                      f'{ip}:{port}', f'{rel}'],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


@sio_a.on('reconnect')
@sio_b.on('reconnect')
def reconnect(new_server):
    global sio, current_sio, accepted
    sio_lock.acquire()
    sio.disconnect()
    if not current_sio:
        sio = sio_b
        current_sio = 1
    else:
        sio = sio_a
        current_sio = 0
    if debug:
        print(f'\nSwitching to new server: {new_server}\n')
    try:
        sio.connect(new_server)
        if accepted:
            sio.emit('login', {
                'ip': p2p_node.host, 'port': p2p_node.port, 'id': p2p_node.id
            })
        if debug:
            print('Switched successfully!\n')
    except exc.ConnectionError:
        accepted = False
    sio_lock.release()


# Run client
if __name__ == '__main__':
    # NOTE: Change this value when debugging
    debug = False

    # Client
    p2p_node = p2p.init_p2p(private_event)
    uri = 'http://127.0.0.1:5000'
    if len(sys.argv) > 1:
        uri = sys.argv[1]
    try:
        print(f'Server URI: {uri}')
        print(f'Personal P2P address: {p2p_node.host}:{p2p_node.port}\n')

        # Connect to chat server
        relay_client.connect(uri)
        while not connected:
            if not connected and not connecting:
                print('Trying to connect to server...')
                relay_client.emit('connect_to_chat')
                connecting = True
        print('Successfully connected to server!')

        # Enter chat room
        user_login()
        while not accepted:
            pass

        # Send messages
        while True:
            send_message()
    except (exc.ConnectionError, exc.BadNamespaceError):
        print('A connection error has occurred, please try to connect again...')
    except KeyboardInterrupt:
        pass
    finally:
        graceful_disconnect()
