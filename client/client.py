import sys
import getopt
import socket
from client_node import ClientNode
from cli import CLI
import json
import traceback


class ClientProfile:
    def __init__(self, client_id=None, host=None, port=None):
        self.client_id = client_id
        self.host = host
        self.port = int(port) if port else socket.gethostbyname(self.host)

    def set_client_id(self, client_id):
        assert client_id is not None
        self.client_id = client_id

    def get_client_id(self):
        return self.client_id

    def get_host_and_port(self):
        return (self.host, int(self.port))


class TrackerProfile:
    def __init__(self, host, port):
        assert host is not None
        assert port is not None
        self.host = host
        self.port = str(port)

    def get_host_and_port(self):
        return (self.host, int(self.port))


class TrackerConnection:
    def __init__(self, profile):
        assert profile is not None
        self.profile = profile
        self.conn_socket = None

    def set_profile(self, profile):
        assert profile is not None
        self.profile = profile

    def create_connection(self):
        self.conn_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.conn_socket.connect(self.profile.get_host_and_port())

    def send(self, data):
        assert self.conn_socket is not None
        self.conn_socket.send(json.dumps(data).encode())

    def receive(self, max_bytes=1024):
        res = self.conn_socket.recv(max_bytes).decode("utf-8")
        return json.loads(res)

    def is_connection_active(self):
        if self.conn_socket is None:
            return False
        try:
            self.send({"api_key": "HEALTH_CHECK"})
            self.receive()
            return True
        except socket.timeout:
            self.close_connection()
            return False

    def close_connection(self):
        self.conn_socket.close()
        self.conn_socket = None


class Client:
    def __init__(self, host=None, port=None):
        self.client_profile = None
        self.tracker_profile = None
        if host and port:
            self.attach_client_profile(ClientProfile(host, port))

        self.tracker_connection = None
        self.client_connection_node = None

    def attach_tracker_profile(self, profile):
        assert isinstance(profile, TrackerProfile)
        self.tracker_profile = profile

    def attach_client_profile(self, profile):
        assert isinstance(profile, ClientProfile)
        self.client_profile = profile

    def show_intro(self):
        print("  Python P2P Chat and File Transfer")
        print("  ")
        print("  Starting P2P Client\n")

        ip, port = self.client_profile.get_host_and_port()
        tip, tport = self.tracker_profile.get_host_and_port()
        print("HOST: {}".format(ip))
        print("PORT: {}".format(port))
        print("TRACKER_IP: {}".format(tip))
        print("TRACKER_PORT: {}".format(tport))

    def open_cli(self):
        self.cli = CLI(self)
        self.cli.run_on_terminal()

    def start(self):
        self.show_intro()
        self.open_cli()

    def check_response(self, received):
        if (
            "api_key" not in received
            or "status" not in received
            or "value" not in received
        ):
            return False
        res_api_key = received["api_key"]
        res_status = int(received["status"])
        res_value = received["value"]
        if res_status != 200 and res_status != 300:
            return False
        return True

    def connect_to_tracker(self):
        if (
            self.tracker_connection is not None
            and self.tracker_connection.is_connection_active()
        ):
            print(
                "Already connected: Tracker {}".format(
                    self.tracker_profile.get_host_and_port()
                )
            )
        else:
            try:
                print("\nConnecting to Network Tracker...")
                self.tracker_connection = TrackerConnection(
                    profile=self.tracker_profile
                )
                self.tracker_connection.create_connection()

                self.tracker_connection.send(
                    {
                        "api_key": "CONNECT",
                        "value": {
                            "ip": self.client_profile.get_host_and_port()[0],
                            "port": self.client_profile.get_host_and_port()[1],
                        },
                    }
                )
                received = self.tracker_connection.receive()
                if not self.check_response(received):
                    err_msg = received["value"] if "value" in received else ""
                    raise Exception()

                client_id = received["value"]
                self.client_profile.set_client_id(client_id)

                print("Connected to Tracker! client id [{}]".format(client_id))

                self.client_connection_node = ClientNode(self.client_profile)
                self.client_connection_node.daemon = True
                self.client_connection_node.start()

                print("\nRequesting Network Peer Information...")
                peer_list = self.request_peer_list()

                print("Received Peer Information!")
                print("\nConnecting to Peers")
                for p in peer_list:
                    if p["id"] != client_id:
                        print(
                            "ID: {}, IP_ADDR: {}, PORT: {}".format(
                                p["id"], p["ip"], p["port"]
                            )
                        )
                        self.client_connection_node.connect(
                            ClientProfile(p["id"], p["ip"], p["port"])
                        )

                print("Done!")

            except Exception as e:
                print(
                    "Error: connection failed: Tracker {}".format(
                        self.tracker_profile.get_host_and_port()
                    )
                )
                print(e)
                traceback.print_exc()

    def request_peer_list(self):
        assert (
            self.tracker_connection is not None
            and self.tracker_connection.is_connection_active()
        )
        self.tracker_connection.send({"api_key": "LIST_PEERS"})
        received = self.tracker_connection.receive()
        if not self.check_response(received):
            print("Failed to retrieve peer information")
            raise Exception()

        data = received["value"]
        my_id = self.client_profile.get_client_id()
        peer_list = filter(lambda p: p["id"] is not my_id, data)
        return peer_list

    def exit_network(self):
        assert (
            self.tracker_connection is not None
            and self.tracker_connection.is_connection_active()
            and self.client_profile.get_client_id() is not None
        )
        self.tracker_connection.send(
            {"api_key": "QUIT", "value": self.client_profile.get_client_id()}
        )
        self.tracker_connection.close_connection()
        self.client_connection_node.shutdown()
        return False

    def shutdown(self):
        self.exit_network()
        sys.exit()

    def __del__(self):
        self.shutdown()


if __name__ == "__main__":
    argv = sys.argv[1:]
    opts, args = getopt.getopt(
        argv, "h", ["client_ip=", "client_port=", "tracker_ip=", "tracker_port="]
    )
    client_ip = None
    client_port = None
    tracker_ip = None
    tracker_port = None

    def pad(str):
        return str.ljust(15)

    for opt, arg in opts:
        if opt == "-h":
            print(pad("--tracker_ip"), "[Required] tracker ip address")
            print(pad("--tracker_port"), "[Required] tracker port number")
            print(pad("--client_ip"), "set client ip address")
            print(pad("--client_port"), "set client port")
            print(
                "e.g. python client.py --client_ip=127.0.0.1 --client_port=3000 --tracker_ip=127.0.0.1 --tracker_port=3000"
            )
            sys.exit()
        if opt == "--client_ip":
            client_ip = arg
        if opt == "--client_port":
            client_port = int(arg)
        if opt == "--tracker_ip":
            tracker_ip = arg
        if opt == "--tracker_port":
            tracker_port = int(arg)

    if client_ip is None:
        client_ip = socket.gethostbyname(socket.gethostname())
    if client_port is None:
        client_port = 3000

    if tracker_ip is None or tracker_port is None:
        print("Error: Missing command argument")
        sys.exit()

    client = Client()
    client.attach_client_profile(ClientProfile(host=client_ip, port=client_port))
    client.attach_tracker_profile(TrackerProfile(tracker_ip, tracker_port))
    client.start()
