import socket
import threading


class Connection(threading.Thread):
    def __init__(self, conn_socket=None):
        super(Connection, self).__init__()
        self.conn_socket = conn_socket
        self.stop_flag = False

    def create_connection(self, op_profile):
        conn_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        conn_socket.connect(op_profile.get_host_and_port())
        self.conn_socket = conn_socket
        return conn_socket

    def send_message(self, message):
        print(message)
        self.conn_socket.send(message.encode())

    def receive_message(self):
        received = self.conn_socket.recv(1024).decode("utf-8")
        print("\nReceived Message: ", received)
        return received

    def close(self):
        self.conn_socket.close()
        self.stop_flag = True

    def run(self):
        while not self.stop_flag:
            self.receive_message()


class ClientNode(threading.Thread):
    def __init__(self, client_profile):
        super(ClientNode, self).__init__()
        assert client_profile is not None
        self.profile = client_profile
        self.connection_list = []
        self.server_socket = None
        self.create_server_socket()
        self.stop_flag = False

    def create_server_socket(self):
        ip, port = self.profile.get_host_and_port()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((ip, port))
        self.server_socket.listen()
        return self.server_socket

    def connect(self, op_profile):
        conn = Connection()
        conn.create_connection(op_profile)
        conn.start()
        self.connection_list.append(conn)

    def broadcast_message(self, message):
        for conn in self.connection_list:
            conn.send_message(message)

    def connec_all(self, profiles):
        for pr in profiles:
            self.connect(pr)

    def clear_connection(self):
        for conn in self.connection_list:
            conn.close()

    def shutdown(self):
        self.clear_connection()
        self.stop_flag = True

    def run(self):
        while not self.stop_flag:
            other_client_node_socket, address = self.server_socket.accept()
            conn = Connection(conn_socket=other_client_node_socket)
            conn.start()
            self.connection_list.append(conn)
