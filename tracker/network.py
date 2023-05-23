import socket
import threading


class TrackerNode(threading.Thread):
    def __init__(self, node_socket, ip, port):
        super(TrackerNode, self).__init__()

        self.node_socket = node_socket
        self.ip = ip
        self.port = port

    def run(self):
        print("tracker node running")
        # while True:
        pass
