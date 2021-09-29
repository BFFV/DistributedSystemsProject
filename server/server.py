from random import choice
from user import User
from migrator import Migrator


class Server:
    def __init__(self) -> None:
        # Client counter
        self.N_CLIENTS_REQUIRED = 2
        self.n_clients = 0

        # Users
        self.users = dict()  # Key: socket ID, Value: Username

        # Usernames set (for quickly checking existence)
        self.usernames = set()

        # Messages
        self.messages = []

        # Migration middleware
        self.migrator = Migrator(self, interval=5)

    def set_params(self, n_clients=2):
        self.N_CLIENTS_REQUIRED = n_clients
        self.n_clients = 0
        self.users = dict()
        self.usernames = set()
        self.messages = []
        print(f'Server initialized (N = {self.N_CLIENTS_REQUIRED})')

    def __getitem__(self, socket_id):
        """ Al acceder a la clase con llave [socket_id], retorna el nombre de usuario."""
        try:
            return self.users[socket_id].username
        except KeyError:
            print(f"El cliente con {socket_id=} no existe!")

    def build_user(self, username, socket_id, *args):
        # args == username, socket_id, ip, port, node_id
        self.n_clients += 1
        self.users[socket_id] = User(username, socket_id, *args)
        self.usernames.add(username)

    def get_user_connections(self, username):
        for user in self.users.values():
            if user.username == username:
                return user.get_connections()

    def find_future_server(self):
        return choice(self.users)
