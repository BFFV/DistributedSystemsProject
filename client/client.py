import socketio
import sys
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


# Print chat & events
def print_state():
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
    print('\nType your message (\':exit:\' to exit program):\n')


# Connection error
@sio.event
def connect_error(msg):
    print(f'\nError connecting to the server!\nDetails: {msg}')


# User login to the chat
def user_login():
    username = input('\nUsername: ')
    print('')
    sio.emit('login', username)


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
    global accepted
    if not chat_is_active:
        print('Type your message (\':exit:\' to exit program):\n')
    message = input()
    print('')
    message = message.strip()
    if message == ':exit:':
        accepted = False
        return False
    if message[:9] == ':private:':
        # message split to check username and non empty msg
        # if correct, emit private to server
        # else return
        pass
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
    # TODO: p2p
    # connect to peer
    # send message
    # disconnect from peer
    pass


# Run client
if __name__ == '__main__':
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
        sio.disconnect()
        print_lock.acquire()
        print('Goodbye!\n')
        print_lock.release()
