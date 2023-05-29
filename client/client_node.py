import socket
import threading


class Connection(threading.Thread):
    def __init__(self, opponent_client_id, socket):
        super(Connection, self).__init__()

        self.opponent_client_id = opponent_client_id
        self.socket = socket

    def run(self):
        while True:
            data = self.socket.recv(1024)
            print("receive: ", repr(data.decode()))


class ClientNode(threading.Thread):
    def __init__(self, client_id, ip, port, file_port):
        super(ClientNode, self).__init__()

        self.client_id = client_id
        self.ip = ip
        self.port = port
        self.file_port = file_port

        self.connection_list = []

    def broadcast_message(self, message):
        pass

    def connect_to_peers(self, peer_list):
        self.node.clear_connection()
        for peer_id, peer_ip, peer_port in peer_list:
            self.node.connect(peer_id, peer_ip, peer_port)

    def connect(self, id, ip_addr, port):
        pass

    def clear_connection(self):
        pass

    def shutdown(self):
        pass

    def run(self):
        while True:
            pass
