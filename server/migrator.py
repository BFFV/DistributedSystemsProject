from threading import Thread
from time import sleep


# Migrator thread
class Migrator:
    def __init__(self, server, interval=30):
        super().__init__()
        self.server = server
        self.interval = interval
        self.timer = Thread(target=self.run, daemon=True)

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
                'ip': self.server.ip, 'port': self.server.port,
                'relay': self.server.relay}
        self.server.sio.emit('create_server', data, room=chosen)

    # Migrate data to new server
    def migrate_data(self, new_server, sid):
        if not self.server.old_server:
            self.server.relay_client.connect(sv.relay)
        self.server.new_server = new_server
        self.server.relay_client.emit('migrating')
        print(f'\nMigrating to {new_server}...\n')
        users_info = {f'{x.ip}:{x.port}': x.username
                      for x in self.server.users.values()}
        self.server.messages_lock.acquire()
        chat_data = {'users': users_info, 'messages': self.server.messages}
        self.server.messages = []
        self.server.messages_lock.release()
        self.server.migrating = True
        self.server.sio.emit('prepare', chat_data, room=sid)

    # Waiting interval
    def wait_interval(self):
        if self.interval == 5:
            print(f'Trying to migrate every {self.interval}s '
                  f'due to no clients!')
        else:
            print(f'Waiting {self.interval}s to migrate')
        sleep(self.interval)
        print('Attempting to migrate...')
