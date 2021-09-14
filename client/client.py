import socketio
import sys
import p2p
from socketio import exceptions as exc
from collections import deque
from threading import Lock


# Socket IO client
sio = socketio.Client()
accepted = False

# Users
count = 1  # User count
usernames = set()  # Usernames (for private messages)

# Chat window
chat = deque()  # Messages (maxlen param for last X messages)
print_lock = Lock()  # Protect the print_state function
chat_is_active = False  # Check if chat is active (N users required)
ask_input = '**Special Commands: [":exit:"-> exit program] ' \
            '[":private: USER MSG" -> send MSG to USER in private]**\n' \
            'Type your message:\n'

# Private message
private_ready = True  # Protect current private message until p2p is ready
private_msg = ''  # Current private message


# Print chat & events
def print_state():
    print('\n')
    print(100 * '*')
    print(46 * ' ' + 'CHAT')
    print(100 * '*')
    if not chat:
        print('No messages!')
    for msg in list(chat):
        print(msg)
    print('\n' + 100 * '*')
    print(f'Users Connected: {count}')
    print(100 * '*')
    print('\n' + ask_input)


# Connection error
@sio.event
def connect_error(msg):
    print(f'\nError connecting to the server!\nDetails: {msg}')
    sys.exit()


# User login to the chat
def user_login():
    username = input('\nUsername (no spaces or ":" allowed): ')
    print('')
    sio.emit('login', {
        'user': username, 'port': p2p_node.port, 'id': p2p_node.id})


@sio.on('graceful_disconnect')
def graceful_disconnect():
    print("Gracefully closing client due to reset!")
    sio.disconnect()
    p2p_node.stop()
    print_lock.acquire()
    print('Goodbye!\n')
    print('Waiting for connections to close...')
    print_lock.release()
    exit()
    #raise KeyboardInterrupt

# Username is valid
@sio.on('accepted')
def login_success():
    global accepted
    accepted = True


# Username is already in use
@sio.on('denied')
def login_failed(msg):
    print(msg)
    user_login()


# Send message to chat
def send_message():
    global accepted, private_msg, private_ready
    if not chat_is_active:
        print(ask_input)
    message = input()
    print('')
    message = message.strip()
    if message == ':exit:':
        accepted = False
        return False
    if message[:9] == ':private:':
        msg_args = message.split()
        if len(msg_args) < 3:
            print('Invalid format for private message!')
            print('\n' + ask_input)
            return True
        username = msg_args[1]
        if username not in usernames:
            print('Invalid username for private message!')
            print('\n' + ask_input)
            return True
        while not private_ready:
            pass
        private_msg = ' '.join(msg_args[2:])
        private_ready = False
        sio.emit('private', username)
        print('Private message sent successfully!')
        print('\n' + ask_input)
    else:
        sio.emit('message', message)
    return True


# Update user count & usernames
@sio.on('users_add')
def add_users(data):
    global count, usernames
    count = data['count']
    usernames |= set(data['users'])


# Update user count & remove user
@sio.on('users_remove')
def remove_user(data):
    global count, usernames
    count = data['count']
    usernames.remove(data['user'])


# Show messages in chat
@sio.on('response')
def receive_message(msg):
    if accepted:
        print_lock.acquire()
        chat.append('\n' + msg)
        print_state()
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
        print(f'Chat is now active!\n')
        print_state()
        print_lock.release()


# Send private message via p2p
@sio.on('send_private_msg')
def send_private_message(data):
    global private_ready
    peer = None
    for node in p2p_node.nodes_outbound:
        if node.host == data['ip'] and node.port == data['port']:
            peer = node
    for node in p2p_node.nodes_inbound:
        if node.host == data['ip'] and node.id == data['id']:
            peer = node
    if not peer:
        # TODO: in production this is not working, it fails to connect
        p2p.connect(p2p_node, data['ip'], data['port'])
        peer = p2p_node.nodes_outbound[-1]
    p2p_node.send_to_node(peer, f'(PRIVATE) {data["origin"]}: {private_msg}')
    private_ready = True


# Callback function for private messaging
def private_event(event, this, other, data):
    if event == 'node_message':
        print_lock.acquire()
        chat.append('\n' + data)
        print_state()
        print_lock.release()


# Run client
if __name__ == '__main__':
    p2p_node = p2p.init_p2p(private_event)
    uri = 'http://127.0.0.1:5000'
    if len(sys.argv) > 1:
        uri = sys.argv[1]
    try:
        sio.connect(uri)
        user_login()
        while not accepted:
            pass
        chatting = True
        while chatting:
            chatting = send_message()
    except KeyboardInterrupt:
        accepted = False
    except exc.ConnectionError:
        accepted = False
    finally:
        graceful_disconnect()
