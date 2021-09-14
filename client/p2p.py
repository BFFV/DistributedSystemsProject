from p2pnetwork.node import Node
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
import socket as soc


class P2PNode(Node):

    # Same as Node class
    def __init__(self, host, port, _id=None,
                 callback=None, max_connections=float('inf')):
        super(P2PNode, self).__init__(
            host, port, _id, callback, max_connections)

    # Hides a log that happens in the original class
    def init_server(self):
        self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.settimeout(10.0)
        self.sock.listen(1)

# Get ip of this machine
def get_my_ip():
    s = soc.socket(soc.AF_INET, soc.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
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


# Initialize p2p node for a client
def init_p2p(callback):
    ipaddr = '127.0.0.1'
    # BUG: p2p no funciona desde diferentes computadores
    ipaddr = get_my_ip()   # Puede que esta línea solucione el problema, falta probarlo
    port = get_free_port()
    node = P2PNode(ipaddr, port, callback=callback)
    node.start()
    return node


# Connect p2p node with a peer
def connect(node, dest_ip, dest_port):
    node.connect_with_node(dest_ip, dest_port)
    print(f"👀 Conexión p2p con {dest_ip}:{dest_port} realizada")
