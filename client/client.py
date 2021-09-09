import socketio
import sys
from socketio import exceptions as exc
from time import sleep
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
ask_input = False  # Check if user needs a reminder for the input
new_user = True  # User just joined the server

# TODO: Avoid repeating input message


# Print chat & events
def print_state():
    print('\n' + 100 * '*')
    print(46 * ' ' + 'CHAT')
    print(100 * '*')
    if not chat:
        print('No messages!')
    for msg in list(chat):
        print(msg)
    print('\n' + 100 * '*')
    print(f'Users Connected: {count}')
    print(100 * '*' + '\n')
    if ask_input:
        print('\n\nType your message (\':exit:\' to exit program):\n')


# Connection error
@sio.event
def connect_error(msg):
    print('\nError connecting to the server!')


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
    global accepted, ask_input, initial
    message = input(
        '\n\nType your message (\':exit:\' to exit program):\n\n ')
    message = message.strip()
    if message == ':exit:':
        accepted = False
        return False
    # TODO: Private p2p
    # If ':private:' in message -> revisar si existe ese username
    # Si existe, emit 'private' al server con el user de destino ya parseado
    # El server tiene el evento on.('private') que recibe el user y le tiene que devolver ip y port a este
    # Con el ip y port mandar el mensaje por p2p
    ask_input = False
    sio.emit('message', message)
    return True


# Update user count
@sio.on('users')
def update_users(data):
    global count, usernames
    count = data['count']
    usernames.add(data['user'])


# Show messages in chat
@sio.on('response')
def receive_message(msg):
    global ask_input
    if accepted:
        print_lock.acquire()
        chat.append('\n' + msg)
        print_state()
        print_lock.release()
        ask_input = True


# Show many messages in chat
@sio.on('msg_queue')
def receive_messages(msgs):
    global new_user, ask_input
    if accepted:
        print_lock.acquire()
        for msg in msgs:
            chat.append('\n' + msg)
        if not new_user:
            print_state()
        print_lock.release()
        new_user = False


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
            sleep(0.2)
            chatting = send_message()
    except KeyboardInterrupt:
        accepted = False
    except exc.ConnectionError:
        accepted = False
    finally:
        sio.disconnect()
        print('\nGoodbye!\n')
