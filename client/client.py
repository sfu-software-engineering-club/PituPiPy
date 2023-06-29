import sys
import getopt
import socket
from client_node import ClientNode
from cli import CLI
import json


class Client:
    def __init__(self, tracker_ip, tracker_port, port, file_port):
        self.tracker_ip = tracker_ip
        self.tracker_port = tracker_port

        self.hostname = socket.gethostname()
        self.ip = socket.gethostbyname(self.hostname)
        self.port = port
        self.file_port = file_port

        self.tracker_socket = None
        self.node = None

    def start(self):
        print("  Python P2P Chat and File Transfer")
        print("  ")
        print("  Starting P2P Client\n")

        print("HOST: {}".format(self.ip))
        print("PORT: {}".format(self.port))
        print("FILE_TRANSFER_PORT: {}\n\n".format(self.file_port))
        print("TRACKER_IP: {}".format(self.tracker_ip))
        print("TRACKER_PORT: {}".format(self.tracker_port))

        self.cli = CLI(self)
        self.cli.cli()

    def check_tracker_connectivity(self):
        if self.tracker_socket is None:
            raise Exception("Error: client is not connected to network")

    def connect_to_tracker(self):
        if self.tracker_socket is not None:
            self.tracker_socket.send("AlreadyConnected: ".encode())
            data = self.tracker_socket.recv(1024)
            data = data.decode('utf-8')
            print("Action denied: ", data)
        else:
            try:
                print("\nConnecting to Network Tracker...")
                self.tracker_socket = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM)
                self.tracker_socket.setsockopt(
                    socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.tracker_socket.connect((self.tracker_ip, self.tracker_port))

                # Receive ACK from tracker with assigned client id
                ack = self.tracker_socket.recv(1024)
                my_client_id = repr(ack.decode())
                self.node = ClientNode(my_client_id, self.ip,
                                    self.port, self.file_port)
                self.node.daemon = True
                self.node.start()
                print("Connected. [client id: {}]".format(my_client_id))

                peer_list = self.request_tracker_list_of_peers()
                print("peer list: ", peer_list)
                # self.node.connect_to_peers(peer_list)

            except Exception as e:
                print(
                    "Error: Could not connect to tracker ({}:{})".format(
                        self.tracker_ip, self.tracker_port
                    )
                )
                print(e)

    def request_tracker_list_of_peers(self):
        """
        send a request message to tracker to retrieve list of peers, and return it

        :return: List<id, ip_addr>

        """
        self.check_tracker_connectivity()

        print("\nRequest list of peers in network to tracker")
        self.tracker_socket.send("LIST_PEERS: ".encode())
        # TODO: receive list of peers from tracker
        data = self.tracker_socket.recv(1024)
        data = data.decode("utf-8")
        data = json.loads(data)
        peer_list = []
        for i in data:
            if i["id"] != self.node.client_id.strip("'"):
                peer_list.append([i["id"], i["ip"], i["port"]])
        return peer_list

    def request_tracker_exit_network(self):
        """
        send a request message to tracker to exit the network

        :return: Boolean
        """
        self.check_tracker_connectivity()
        # TODO
        return False

    def print_help(self):
        def pad(str):
            return str.ljust(20)

        print("\n")
        print(pad("  Options"))
        print(pad("/connect"), "--", "connect to tracker")
        print(pad("/status"), "--", "show the current network connection status")
        print(pad("/log_file_output [location]"),
              "--", "logging file location")
        print(pad("/send_message [message]"),
              "--", "send a message to network")
        print(pad("/exit"), "--", "exit from network")
        print(pad("/shutdown"), "--", "terminate the client")

    def shutdown(self):
        self.request_tracker_exit_network()
        self.node.shutdown()
        if self.tracker_socket is not None:
            self.tracker_socket.close()
        sys.exit()


if __name__ == "__main__":
    argv = sys.argv[1:]
    opts, args = getopt.getopt(
        argv, "h", ["client_port=", "client_file_port=",
                    "tracker_ip=", "tracker_port="]
    )
    tracker_ip = None
    tracker_port = None
    port = None
    fport = None

    def pad(str):
        return str.ljust(15)

    for opt, arg in opts:
        if opt == "-h":
            print(pad("--tracker_ip"), "tracker ip address")
            print(pad("--tracker_port"), "tracker port number")
            print(pad("--client_port"), "set client port")
            print(pad("--client_file_port"), "set client file transfer port")
            print(
                "e.g. python client.py --client_port=3000 --client_file_port=3001 --tracker_ip=127.0.0.1 --tracker_port=2500"
            )
            sys.exit()
        if opt == "--tracker_ip":
            tracker_ip = arg
        if opt == "--tracker_port":
            tracker_port = int(arg)
        if opt == "--client_port":
            port = int(arg)
        if opt == "--client_file_port":
            fport = int(arg)

    client_params = [tracker_ip, tracker_port, port, fport]

    if None in client_params:
        print("Error: Missing command argument")
        sys.exit()

    client = Client(*client_params)
    client.start()