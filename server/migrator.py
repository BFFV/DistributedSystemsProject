from threading import Thread
from time import sleep


# Migrator thread
class Migrator(Thread):
    def __init__(self, server, interval=30):
        super().__init__()
        self.server = server
        self.interval = interval

        # TODO: only start if needed
        self.start()

    # Start migration to client machine
    def run(self) -> None:
        # Need at least one user to migrate
        while not len(self.server.users):
            self.wait_interval()
        # TODO: Spawn new server in chosen client

    # Migrate data to new server
    def migrate_data(self):
        # TODO: Connect client socket to new server
        # TODO: Send usernames/ip_port and messages to new server
        # TODO: Clear messages and tell clients to connect to new server (lock)
        # TODO: Wait for 2 seconds while collecting delayed messages
        # TODO: Send delayed messages to new server and then exit()
        pass

    # Waiting interval
    def wait_interval(self):
        print(f'Waiting {self.interval}s to migrate')
        sleep(self.interval)
        print('Attempting to migrate...')


# Run migrator (testing only)
if __name__ == "__main__":
    mig = Migrator(None, 2)
