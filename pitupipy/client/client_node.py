import socket
import threading
import utils
from .cli import CLI


class PeerConnection(threading.Thread):
    def __init__(
        self, id=None, name=None, ip=None, port=None, peer_socket=None, cli=None
    ):
        assert cli is not None
        super(PeerConnection, self).__init__()
        self.id = id
        self.name = name
        self.ip = ip
        self.port = port
        self.peer_socket = peer_socket
        self.cli = cli
        self.termination_flag = False

    def establish(self, id, name, ip, port):
        peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        peer_socket.connect((ip, port))
        peer_socket.send(
            utils.json_encode(
                {
                    "api_key": "CONNECT",
                    "value": {
                        "id": id,
                        "name": name,
                        "ip": ip,
                        "port": port,
                    },
                }
            )
        )
        res = utils.json_decode(peer_socket.recv(1024))
        if res["status_code"] != 200:
            raise Exception(
                "Connection Refused. {}, {}, {}:{}".format(id, name, ip, port)
            )
        self.id = id
        self.ip = ip
        self.name = name
        self.port = port
        self.peer_socket = peer_socket

    def send_message(self, message):
        self.peer_socket.send(
            utils.json_encode(
                {
                    "api_key": "MESSAGE",
                    "value": {"message": message},
                }
            )
        )

    def receive_message(self, received):
        message = received["value"]["message"]
        self.cli.add_body_text("[{}] {}".format(self.name, message))

    def close(self):
        self.termination_flag = True
        self.stop()

    def run(self):
        while not self.termination_flag:
            received = utils.json_decode(self.peer_socket.recv(1024))
            if received["api_key"] == "MESSAGE":
                self.receive_message(received)


class ClientNode(threading.Thread):
    def __init__(self, id, name, port, cli=None):
        assert cli is not None
        super(ClientNode, self).__init__()
        self.name = name
        self.id = id
        self.port = port
        self.cli = cli
        self.connection_list = []
        # Client server socket
        ip, port = (utils.local_ip_address(), self.port)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((ip, port))
        self.server_socket.listen()

        self.termination_flag = False

    def connect(self, peer_id, peer_name, peer_ip, peer_port):
        peer_conn = PeerConnection(cli=self.cli)
        peer_conn.establish(id=peer_id, name=peer_name, ip=peer_ip, port=peer_port)
        peer_conn.daemon = True
        peer_conn.start()
        self.connection_list.append(peer_conn)

    def send_message_to_all(self, message):
        for conn in self.connection_list:
            conn.send_message(message)

    def send_message(self, opponent_id, message):
        for conn in self.connection_list:
            if conn.id == opponent_id:
                conn.send_message(message)
                break

    def close(self):
        for conn in self.connection_list:
            conn.close()
        self.termination_flag = True

    def run(self):
        while not self.termination_flag:
            # Accept incoming connection request
            socket, _ = self.server_socket.accept()
            res = utils.json_decode(socket.recv(1024))
            p = res["value"]
            peer_conn = PeerConnection(
                id=p["id"],
                name=p["name"],
                ip=p["ip"],
                port=p["port"],
                cli=self.cli,
                peer_socket=socket,
            )
            peer_conn.daemon = True
            peer_conn.start()
            socket.send(
                utils.json_encode(
                    {
                        "api_key": "CONNECT",
                        "status_code": 200,
                    }
                )
            )
            self.connection_list.append(peer_conn)
            self.cli.add_body_text("{} joined the network".format(p["name"]))
