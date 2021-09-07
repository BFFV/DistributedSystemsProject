import socketio
import re


# Socket IO client
sio = socketio.Client()

# @sio.event
# def connect():
#     #sio.emit('
# connect', {'data': 'trying to connect'})
#     pass


# from prettytable import PrettyTable
# tabla_mensajes = PrettyTable()
# tabla_mensajes.field_names = ["Usuario", "Mensaje"]
    
@sio.event
def login(username):
    sio.emit('login', {'userKey': 'streaming_api_key'})
    sio.emit('message', {'data': 'User Connected'})

@sio.event
def connect_error():
    print("The connection failed!")

@sio.event
def message(data):
    print('I received a message!')

@sio.on('response')
def on_message(data):
    # tabla_mensajes.add_row([data["user"], data["text"]])
    # print(tabla_mensajes)
    print(f'\n{data["user"]}: {data["text"]} + \n')

@sio.on('users')
def on_message(data):
    print(f"\nCantidad usuarios: {data['user_count']} \n")

def send_message(username):
    message = input("")
    sio.emit('message', {'text': message, 'user': username})

    send_message(username)

# Run client
if __name__ == '__main__':
    # try:
    #     sio.connect('http://127.0.0.1:5000')
    # except TypeError:
    #     print("No se logro conectar al servidor")
    # username = "user name"
    # while not re.match("^[a-zA-Z0-9_.-]+$", username):
    #     username = input("Ingrese su nombre de usuario: ")
    #     if not re.match("^[a-zA-Z0-9_.-]+$", username):
    #         print("Ingrese caracteres alfanumericos o _.-")
    sio.connect('http://127.0.0.1:5000')
    username = input('Username: ')
    # sio.
    try:
        while True:
            send_message(username)
    except KeyboardInterrupt:
        sio.disconnect()
