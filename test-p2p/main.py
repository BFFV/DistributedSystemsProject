import sys
import time
sys.path.insert(0, '..') # Import the files where the modules are located

from p2pnode import MyOwnPeer2PeerNode

node_1 = MyOwnPeer2PeerNode("127.0.0.1", 8001, 1)
node_2 = MyOwnPeer2PeerNode("127.0.0.1", 8002, 2)
node_3 = MyOwnPeer2PeerNode("127.0.0.1", 8003, 3)

time.sleep(1)

node_1.start()
node_2.start()
node_3.start()

time.sleep(1)

node_1.connect_with_node('127.0.0.1', 8002)
node_2.connect_with_node('127.0.0.1', 8003)
node_3.connect_with_node('127.0.0.1', 8001)

time.sleep(2)

node_2.send_to_nodes("message: Hi there node 1!")

node_2.send_to_nodes("message: Hi there node 2!")

node_3.send_to_nodes("message: Hi there node 3!")

time.sleep(5)

node_1.stop()
node_2.stop()
node_3.stop()
print('end test')