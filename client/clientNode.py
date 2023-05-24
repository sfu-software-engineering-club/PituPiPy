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


class ClientNode:
    def __init__(self, client_id, ip, port, file_port):
        self.client_id = client_id
        self.ip = ip
        self.port = port
        self.file_port = file_port

        self.connection_list = []

    def broadcast_message(self, message):
        pass

    def create_new_connection(self, id, ipAddr):
        pass

    def clear_connection(self):
        pass

    def shutdown(self):
        pass
