from migrator import Migrator
from random import choice
from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM
from threading import Lock
from user import User


# Chat server
class Server:
    def __init__(self, ip, port, sio, sio_client, relay_client, relay_uri,
                 twin_client, twin_uri, start=True):
        # Client counter
        self.N_CLIENTS_REQUIRED = 2
        self.n_clients = 0

        # Users
        self.users = dict()  # Key: socket ID, Value: User object
        self.rep_users = dict()  # Key: rep_username, Value: User object
        self.old_users = dict()  # Key: "ip:port", Value: (username, node_id)

        # Usernames set (for quickly checking existence)
        self.usernames = set()

        # Messages
        self.messages = []
        self.messages_lock = Lock()

        # Migration thread
        self.migrating = False
        self.migrator = Migrator(self)
        if start:
            self.migrator.timer.start()
        self.can_migrate = True
        self.attempting = False
        self.emergency = False

        # Connection data
        self.ip = ip
        self.port = port
        self.sio = sio
        self.client = sio_client

        # Relay server
        self.relay = relay_uri
        self.relay_client = relay_client

        # Old server
        self.old_server = ''

        # New server
        self.new_server = ''

        # Twin server
        self.twin_client = twin_client
        self.twin_uri = twin_uri

    # Update params for server
    def set_params(self, n_clients=2):
        self.N_CLIENTS_REQUIRED = n_clients
        self.n_clients = 0
        self.users = dict()
        self.usernames = set()
        self.messages = []
        print(f'Server initialized (N = {self.N_CLIENTS_REQUIRED})')

    # Returns username by key [socket_id]
    def __getitem__(self, socket_id):
        try:
            return self.users[socket_id].username
        except KeyError:
            print(f'Client with SID {socket_id} does not exist!')

    # Create new user
    def build_user(self, username, socket_id, *args):
        # args == username, socket_id, ip, port, node_id
        self.n_clients += 1
        self.users[socket_id] = User(username, socket_id, *args)
        self.usernames.add(username)

    # Get connection data from user
    def get_user_connections(self, username):
        for user in self.users.values():
            if user.username == username:
                return user.get_connections()
        if username in self.rep_users:
            return self.rep_users[username]

    # Choose new client to migrate the server
    def find_future_server(self):
        return choice(list(self.users.keys()))

    # Choose new client to migrate the server on SIGINT
    def find_emergency_server(self, sid):
        print(list(self.users.keys()))
        print([u for u in self.users.keys() if u != sid])
        return choice([u for u in self.users.keys() if u != sid])


# Get local ip of the server
def get_local_ip():
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


# Get a free port in this machine
def get_free_port():
    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind(('', 0))
    free_port = sock.getsockname()[1]
    sock.close()
    return free_port
