import builtins
from threading import Thread
from time import sleep


# Migrator thread
class Migrator:
    def __init__(self, server, interval=30):
        self.server = server
        self.interval = interval
        self.timer = Thread(target=self.run, daemon=True)

    # Start migration to client machine
    def run(self):
        # Migration timer cycle
        chosen = None
        waiting = True
        while waiting:
            self.wait_interval()
            while not self.server.can_migrate:
                sleep(0.5)
            while self.server.shutdown:
                sleep(0.5)
            self.server.attempting = True
            self.print('Attempting to migrate...')
            chosen = self.server.find_future_server()
            if not chosen and not self.server.shutdown:
                addr = f'http://{self.server.ip}:{self.server.port}'
                if self.server.twin_uri:
                    self.server.twin_client.emit('twin', addr)
                    self.server.can_migrate = False
                self.server.attempting = False
            elif not self.server.shutdown:
                waiting = False

        # Create new server from client
        data = {'n_clients': self.server.N_CLIENTS_REQUIRED,
                'ip': self.server.ip, 'port': self.server.port,
                'relay': self.server.relay, 'twin': self.server.twin_uri}
        self.server.sio.emit('create_server', data, room=chosen)

    # Migrate data to new server
    def migrate_data(self, new_server, sid):
        self.server.new_server = new_server
        self.print(f'\nMigrating to {new_server}...\n')
        users_info = {f'{x.ip}:{x.port}': x.username
                      for x in self.server.users.values()}
        self.server.messages_lock.acquire()
        chat_data = {'users': users_info,
                     'usernames': list(self.server.usernames),
                     'rep_users': self.server.rep_users,
                     'messages': self.server.messages}
        self.server.messages = []
        self.server.messages_lock.release()
        self.server.migrating = True
        self.server.sio.emit('prepare', chat_data, room=sid)

    # Waiting interval
    def wait_interval(self):
        print(f'Waiting {self.interval}s to migrate')
        sleep(self.interval)

    # Mod print to add server location
    def print(self, *args, **kwargs):
        builtins.print(
            f'||| {self.server.ip}:{self.server.port} |||', *args, **kwargs)
