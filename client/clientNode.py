import socket
import threading


class Connection(threading.Thread):
    pass


class ClientNode(threading.Thread):
    def __init__(self, node_socket, ip, port, file_port):
        super(ClientNode, self).__init__()

        self.node_socket = node_socket
        self.ip = ip
        self.port = port
        self.file_port = file_port

    def run(self):
        print("client node running")
        # while True:
        pass
