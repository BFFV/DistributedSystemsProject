from threading import Thread
from time import sleep


class Migrator(Thread):
    def __init__(self, sever, interval=30):
        super().__init__()

        self.server = sever
        self.interval = interval
        self.start()

    def run(self) -> None:
        # No podemos migrar si no hay algún usuario conectado
        while not len(self.server.users):
            self.wait_interval()

        information_dict = self.server.__dict__
        print(information_dict)

    def wait_interval(self):
        print(f"Esperando {self.interval}s para migrar")
        sleep(self.interval)
        print("Intentando migración...")


if __name__ == "__main__":
    mig = Migrator(None, 2)
