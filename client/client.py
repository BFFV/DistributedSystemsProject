import socketio
import sys
from socketio import exceptions as exc
from time import sleep
from collections import deque


# Socket IO client
sio = socketio.Client()
accepted = False
active = True

# Chat window
chat = deque(maxlen=10)
count = 1
event = ''


# Print chat & events
def print_state():
    print(2 * '\n')
    print(event)
    print('------------------------------------')
    print(f'Users Connected: {count}')
    print('------------------------------------')
    if not chat:
        print('No messages!')
    for msg in chat:
        print(msg)
    print('------------------------------------')
    print('\n\n(your input)')


# Connection error
@sio.event
def connect_error(msg):
    print('Error connecting to the server!')


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
    global active
    message = input(
        '\n\nType your message (\':exit:\' to exit program):\n\n>> ')
    message = message.strip()
    if message == ':exit:':
        active = False
        return False
    sio.emit('message', message)
    return True


# Update user count & show state messages
@sio.on('users')
def update_count(data):
    global event, count
    if active:
        event = data['msg']
        count = data['count']
        print_state()
        event = ''


# Show messages in chat
@sio.on('response')
def receive_message(msg):
    if active:
        chat.append('\n' + msg)
        print_state()


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
        active = False
    except exc.ConnectionError:
        active = False
    finally:
        sio.disconnect()
        print('\nGoodbye!')
