import os
import p2p
import socketio
import subprocess
import sys
from collections import deque
from socketio import exceptions as exc
from threading import Lock


# Socket IO client
sio = socketio.Client()
connected = False
accepted = False

# Users
count = 1  # User count

# Chat window
chat = deque()  # Messages (maxlen param for last X messages)
print_lock = Lock()  # Protect the print_state function
chat_is_active = False  # Check if chat is active (N users required)
ask_input = f'{54 * "-"}\nSpecial Commands:{36 * " "}|\n{53 * " "}|\n' \
            f'"$exit" -> exit program{30 * " "}|\n' \
            f'"$private USER MSG" -> send MSG to USER in private' \
            f'{3 * " "}|\n' \
            f'"$reset -N" -> reset server with N required users' \
            f'{4 * " "}|\n{54 * "-"}\n\n' \
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
@sio.event
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
@sio.on('exit')
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
    p2p_node.stop()
    exit()


# Username is valid
@sio.on('accepted')
def login_success():
    global accepted
    accepted = True


# Username is already in use
@sio.on('denied')
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
            sio.emit('message', ' '.join(msg[:2]))  # To protect private text
            return
    if not accepted:  # Server was reset
        print_lock.acquire()
        print('Closing client due to server reset!\n')
        print_lock.release()
        raise KeyboardInterrupt
    sio.emit('message', message)


# Update user count
@sio.on('users')
def users_count(data):
    global count
    count = data


# Show messages in chat
@sio.on('response')
def receive_message(msg):
    if accepted:
        print_lock.acquire()
        chat.append('\n' + msg)
        print_state()
        print_lock.release()


# Show event messages (usually input errors)
@sio.on('event')
def receive_event(msg):
    if accepted:
        print_lock.acquire()
        print(msg)
        print('\n' + ask_input)
        print_lock.release()


# Show many messages in chat
@sio.on('msg_queue')
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
@sio.on('send_private_msg')
def send_private_message(data):
    global private_ready
    private_ready = False
    peer = p2p.get_peer(p2p_node, data)
    if not peer:
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
@sio.on('connect_to_chat')
def connect_to_chat(data):
    global connected
    sio.disconnect()
    sio.sleep(1)
    sio.connect(f'http://{data[0]}:{data[1]}')
    connected = True


# Create new server from this client
@sio.on('create_server')
def create_server(data):
    server_port = p2p.get_free_port()
    current_dir = os.path.dirname(os.path.realpath(__file__))
    n_clients = data['n_clients']
    ip = data['ip']
    port = data['port']
    subprocess.Popen(['python3', f'{current_dir}/../server/chat_server.py',
                      f'-{n_clients}', f'{server_port}', 'new', f'{ip}:{port}'],
                     stdout=None, stderr=subprocess.DEVNULL)

# TODO: Reconnect to new server (after migration)


# Run client
if __name__ == '__main__':
    p2p_node = p2p.init_p2p(private_event)
    uri = 'http://127.0.0.1:5000'
    if len(sys.argv) > 1:
        uri = sys.argv[1]
    try:
        print(f'Server URI: {uri}')
        print(f'Personal P2P address: {p2p_node.host}:{p2p_node.port}\n')

        # Connect to chat server
        sio.connect(uri)
        sio.emit('connect_to_chat')
        while not connected:
            pass
        user_login()
        while not accepted:
            pass
        while True:
            send_message()
    except (KeyboardInterrupt, exc.ConnectionError):
        pass
    finally:
        graceful_disconnect()
