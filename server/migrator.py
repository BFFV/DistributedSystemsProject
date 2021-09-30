from threading import Thread
from time import sleep


# Migrator thread
class Migrator(Thread):
    def __init__(self, server, interval=30):
        super().__init__()
        self.server = server
        self.interval = interval
        self.daemon = True

    # Start migration to client machine
    def run(self):
        # Initial timer
        self.wait_interval()
        self.interval = 5

        # Need at least one user to migrate
        while not len(self.server.users):
            self.wait_interval()

        # Create new server from client
        chosen = self.server.find_future_server()
        data = {'n_clients': self.server.N_CLIENTS_REQUIRED,
                'ip': self.server.ip, 'port': self.server.port}
        self.server.sio.emit('create_server', data, room=chosen)

    # Migrate data to new server
    def migrate_data(self, new_server):
        print(f'\nMigrating to {new_server}...\n')
        self.server.client.connect(new_server)
        users_info = {f'{x.ip}:{x.port}': x.username
                      for x in self.server.users.values()}
        self.server.messages_lock.acquire()
        chat_data = {'users': users_info, 'messages': self.server.messages,
                     'relay': self.server.relay}
        self.server.messages = []
        self.server.messages_lock.release()
        self.server.client.emit('prepare', chat_data)
        self.server.sio.emit('reconnect', new_server)
        # TODO: Wait for 2 seconds while collecting delayed messages
        # TODO: Send delayed messages to new server and then exit()
        self.server.client.disconnect()
        print('\nFinished migrating, exiting server...\n')

    # Waiting interval
    def wait_interval(self):
        if self.interval < 30:
            print(f'Trying to migrate every {self.interval}s '
                  f'due to no clients!')
        else:
            print(f'Waiting {self.interval}s to migrate')
        sleep(self.interval)
        print('Attempting to migrate...')
