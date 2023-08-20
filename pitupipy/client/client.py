import sys
import socket
import traceback
import json
import utils
from .client_node import ClientNode
from .cli import CLI


class Network:
    class NetworkException(Exception):
        @staticmethod
        def connection_failure(message=""):
            raise Network.NetworkException(message)

    def __init__(self):
        self.network_name = None
        self.tracker_ip = None
        self.tracker_port = None
        self.client_id = None
        self.client_name = None
        self.client_port = None
        self.conn_socket = None
        self.clinet_connection = None
        self.is_alive = False

    def establish_connection(self, client_name, client_port, tracker_ip, tracker_port):
        self.is_alive = False
        self.conn_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.conn_socket.connect((tracker_ip, tracker_port))

            res = self.api_request(
                {
                    "api_key": "CONNECT",
                    "value": {
                        "name": client_name,
                        "ip": utils.local_ip_address(),
                        "port": client_port,
                    },
                }
            )
            self.tracker_ip = tracker_ip
            self.tracker_port = tracker_port
            self.network_name = res["value"]["network_name"]
            self.client_id = res["value"]["client_id"]
            self.client_name = client_name
            self.client_port = client_port

            res = self.api_request({"api_key": "LIST_PEERS"})
            self.client_connection = ClientNode(
                id=self.client_id, name=client_name, port=client_port
            )
            self.client_connection.daemon = True
            self.client_connection.start()
            peer_list = filter(lambda p: p["id"] != self.client_id, res["value"])
            for p in peer_list:
                self.client_connection.connect(
                    peer_id=p["id"],
                    peer_name=p["name"],
                    peer_ip=p["ip"],
                    peer_port=p["port"],
                )

            self.is_alive = True

        except ConnectionRefusedError as e:
            raise Network.NetworkException.connection_failure(e)

    def network_peers(self):
        assert isinstance(self.conn_socket, socket.socket)
        res = self.api_request({"api_key": "LIST_PEERS"})
        peer_list = res["value"]
        return peer_list

    def broadcast_message(self, message):
        try:
            self.client_connection.send_message_to_all(message)
        except Exception as e:
            raise Network.NetworkException(e)

    def private_message(self, opponent_id, message):
        try:
            self.client_connection.send_message(opponent_id, message)
        except Exception as e:
            raise Network.NetworkException(e)

    def who_is(self, peer_id):
        try:
            return self.client_connection.get_name_by_id(peer_id)
        except Exception as e:
            raise Network.NetworkException(e)

    def is_network_alive(self):
        return self.is_alive

    def api_request(self, data):
        assert isinstance(self.conn_socket, socket.socket)
        self.conn_socket.send(utils.json_encode(data))
        response = utils.json_decode(self.conn_socket.recv(1024))
        if response["status_code"] != 200:
            raise Network.NetworkException.connection_failure(
                "Error Code", str(response["status_code"])
            )
        return response

    def close(self):
        if self.is_alive:
            self.client_connection.close()
            self.conn_socket.close()
        self.is_alive = False

    def __del__(self):
        self.close()


class Client:
    def __init__(self):
        self.ip = utils.local_ip_address()
        self.port = None
        self.cli = CLI()
        self.network = Network()
        # Flags
        self.termination_flag = False

    def listen(self, port):
        assert isinstance(port, int)
        self.port = port
        self.cli.add_header_text("PituPiPy")
        self.cli.add_header_text("Chat and File Transfer in P2P network")
        self.cli.set_network_status_text("Not Connected.")

        while self.termination_flag is False:
            input = self.cli.input()
            self.execute_cmd(input)

    """
    Client Commands
    """

    def execute_cmd(self, input):
        inputs = input.split(" ")
        cmd = inputs[0]
        args = inputs[1 : len(inputs)]
        try:
            if cmd == "help":
                self.cmd_help()
            elif cmd == "status":
                self.cmd_network_status()
            elif cmd == "exit":
                self.cmd_exit_network()
            elif cmd == "q" or cmd == "shutdown":
                self.cmd_shutdown()
            elif cmd == "connect":
                self.cli.set_command_prompt("Your name >> ")
                cname = self.cli.input()
                self.cli.set_command_prompt("Tracker IP >> ")
                tIp = self.cli.input()
                self.cli.set_command_prompt("Tracker PORT >> ")
                tPort = self.cli.input()
                self.cli.reset_command_prompt()
                self.cmd_connect(client_name=cname, tracker_ip=tIp, tracker_port=tPort)
            elif cmd == "send_message":
                if len(args) > 0:
                    self.cmd_send_message(args[0])
                else:
                    self.cli.set_command_info("No message provided.")
            elif cmd == "whisper":
                if len(args) == 0:
                    self.cli.set_command_info("No client ID provided for whispering.")
                elif len(args) == 1:
                    self.cli.set_command_info("No message provided for whispering.")
                self.cmd_send_private_message(opponent_id=args[0], message=args[1])
            else:
                self.cli.set_command_info("Invalid command.")

        except Exception as e:
            raise e
            # self.cli.set_command_info("!Error occured: {}".format(e))

    def cmd_help(self):
        self.cli.set_command_info(
            """Command Options
            /connect                        -- connect to a P2P network          
            /status                         -- show the list of clients in a network
            /send_message [message]         -- send a public message to network
            /whisper [client_id] [message]  -- send a message to a single opponent client
            /exit                           -- exit the network
            /q or /shutdown                 -- close the program
        """
        )

    def cmd_connect(self, client_name, tracker_ip, tracker_port):
        if self.network.is_network_alive():
            self.cli.set_command_info(
                "Already connected to a network. To exit the current network, enter [/exit]."
            )
        else:
            try:
                self.cli.set_network_status_text("Connecting to Network...")
                self.network.establish_connection(
                    client_name=client_name,
                    client_port=self.port,
                    tracker_ip=tracker_ip,
                    tracker_port=int(tracker_port),
                )
                self.cli.set_network_status_text(
                    "Network Connected: [{}] ip:{}, port:{}".format(
                        self.network.network_name, tracker_ip, tracker_port
                    )
                )
                self.cli.add_header_text("Client Info:")
                self.cli.add_header_text(
                    "{}, ip:{}, port:{}".format(client_name, self.ip, self.port)
                )
                self.cmd_network_status()
            except Network.NetworkException as e:
                self.cli.set_network_status_text("Connection Refused. {}".format(e))

    def cmd_network_status(self):
        if self.network.is_network_alive() is False:
            self.cli.set_command_info("You have not connected to a network.")
        else:
            peer_list = self.network.network_peers()
            info = ""
            for peer in peer_list:
                info += "{}, {}: {}\n".format(peer["name"], peer["ip"], peer["port"])
            self.cli.set_command_info(info)

    def cmd_send_message(self, message):
        if self.network.is_network_alive():
            self.network.broadcast_message(message)
            self.cli.add_body_text("[{}] {}".format(self.network.client_name, message))

    def cmd_send_private_message(self, opponent_id, message):
        if self.network.is_network_alive():
            self.network.private_message(opponent_id=opponent_id, message=message)
            self.cli.add_body_text(
                "[{}] >> [{}] {}".format(
                    self.network.client_name, self.network.who_is(opponent_id), message
                )
            )

    def cmd_exit_network(self):
        if self.network.is_network_alive() is False:
            self.cli.set_command_info("You have not connected to a network.")
        else:
            self.network.close()
            self.cli.set_network_status_text("Not Connected.")

    def cmd_shutdown(self):
        if self.network.is_network_alive():
            self.network.close()
        sys.exit()

    def __del__(self):
        self.cmd_shutdown()
