import socket
import threading
import utils
from .cli import CLI


class PeerConnection(threading.Thread):
    def __init__(
        self,
        id=None,
        name=None,
        ip=None,
        port=None,
        client_node=None,
        peer_socket=None,
        cli=None,
    ):
        assert client_node is not None
        assert cli is not None
        super(PeerConnection, self).__init__()
        self.id = id
        self.name = name
        self.ip = ip
        self.port = port
        self.peer_socket = peer_socket
        self.cli = cli
        self.client_node = client_node
        self.termination_flag = False

    def establish(
        self, req_id, req_name, req_ip, req_port, peer_id, peer_name, peer_ip, peer_port
    ):
        peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        peer_socket.connect((peer_ip, peer_port))
        peer_socket.send(
            utils.json_encode(
                {
                    "api_key": "CONNECT",
                    "value": {
                        "req_id": req_id,
                        "req_name": req_name,
                        "req_ip": req_ip,
                        "req_port": req_port,
                    },
                }
            )
        )
        res = utils.json_decode(peer_socket.recv(1024))
        if res["status_code"] != 200:
            raise Exception(
                "Connection Refused. {}, {}, {}:{}".format(
                    peer_id, peer_name, peer_ip, peer_port
                )
            )
        self.id = peer_id
        self.ip = peer_ip
        self.name = peer_name
        self.port = peer_port
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

    def receive_message(self, message):
        message_text = message["value"]["message"]
        self.cli.add_body_text("[{}] {}".format(self.name, message_text))

    def close_connection(self):
        self.client_node.remove_peer_connection(self)
        self.peer_socket.close()
        self.termination_flag = True

    def run(self):
        while not self.termination_flag:
            received = self.peer_socket.recv(1024)
            if not received:
                self.close_connection()
            else:
                message = utils.json_decode(received)
                if message["api_key"] == "MESSAGE":
                    self.receive_message(message)


class ClientNode(threading.Thread):
    def __init__(self, id, name, port, cli=None):
        assert cli is not None
        super(ClientNode, self).__init__()
        self.name = name
        self.id = id
        self.ip = utils.local_ip_address()
        self.port = port
        self.cli = cli
        self.connection_list = []
        # Client server socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.ip, self.port))
        self.server_socket.listen()

        self.termination_flag = False

    def connect(self, peer_id, peer_name, peer_ip, peer_port):
        peer_conn = PeerConnection(cli=self.cli, client_node=self)
        peer_conn.establish(
            req_id=self.id,
            req_name=self.name,
            req_ip=self.ip,
            req_port=self.port,
            peer_id=peer_id,
            peer_name=peer_name,
            peer_ip=peer_ip,
            peer_port=peer_port,
        )
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
            conn.close_connection()
        self.termination_flag = True

    def remove_peer_connection(self, exit_peer_connection):
        new_conns = []
        for conn in self.connection_list:
            if conn.id != exit_peer_connection.id:
                new_conns.append(conn)
        self.connection_list = new_conns
        self.cli.add_body_text(
            "{} exited from the network.".format(exit_peer_connection.name)
        )

    def run(self):
        while not self.termination_flag:
            # Accept incoming connection request
            socket, _ = self.server_socket.accept()
            res = utils.json_decode(socket.recv(1024))

            if res["api_key"] == "CONNECT":
                p = res["value"]
                peer_conn = PeerConnection(
                    id=p["req_id"],
                    name=p["req_name"],
                    ip=p["req_ip"],
                    port=p["req_port"],
                    cli=self.cli,
                    peer_socket=socket,
                    client_node=self,
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
                self.cli.add_body_text("{} joined the network.".format(p["req_name"]))
