# User model
class User:
    def __init__(self, username, socket_id, ip, port, node_id):
        # Identification
        self.username = username
        self.socket_id = socket_id

        # Connections
        self.ip = ip
        self.port = port
        self.node_id = node_id

    # Get connection data from user
    def get_connections(self):
        return self.ip, self.port, self.node_id
