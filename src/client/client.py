import sys
import getopt
import socket
from clientNode import ClientNode


class Client:
    def __init__(self, tracker_ip, tracker_port, port, file_port):
        self.tracker_ip = tracker_ip
        self.tracker_port = tracker_port

        self.hostname = socket.gethostname()
        self.ip = socket.gethostbyname(self.hostname)
        self.port = port
        self.file_port = file_port

        self.socket = None
        self.node = None

    def start(self):
        print("  Python P2P Chat and File Transfer")
        print("  ")
        print("  Starting P2P Client\n")

        print("HOST: {}".format(self.ip))
        print("PORT: {}".format(self.port))
        print("FILE_TRANSFER_PORT: {}\n\n".format(self.file_port))

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.ip, self.port))
        self.socket.listen()

        self.node = ClientNode(self.socket, self.ip, self.port, self.file_port)
        self.node.daemon = True
        self.node.start()

        self.cli()

    def request_connection_to_network(self):
        # send connection request to network tracker
        pass

    def request_to_exit_network(self):
        # send connection removal request to network tracker
        pass

    def query_list_of_peers_to_tracker(self):
        # request connected peer information to tracker
        pass

    def send_message_to_network(self):
        # send chat message to network
        pass

    def print_help(self):
        def pad(str):
            return str.ljust(20)

        print("\n")
        print(pad("  Options"))
        print(pad("/connect"), "--", "connect to network")
        print(pad("/list_peers"), "--", "list all the peer IPs in the network")
        print(pad("/send_message"), "--", "send a message to network")
        print(pad("/exit"), "--", "exit from network")
        print(pad("/shutdown"), "--", "terminate the client")

    def shutdown():
        # send connection removal request to network tracker and shutdown the instance
        # self.request_to_exit_network()
        pass

    def cli(self):
        COMMAND_PROMPT = "\nCOMMAND? [/q or /shutdown] >> /"
        self.print_help()
        while True:
            print("\n")
            print(COMMAND_PROMPT, end="")
            cmd = str(input())

            if cmd == "help":
                self.print_help()

            elif cmd == "connect":
                pass

            elif cmd == "list_peers":
                pass

            elif cmd == "send_message":
                pass

            elif cmd == "exit":
                pass

            elif cmd == "/q" or cmd == "shutdown":
                self.shutdown()

            else:
                print("Error: unknown command: {}".format(cmd))


if __name__ == "__main__":
    argv = sys.argv[1:]
    opts, args = getopt.getopt(
        argv, "h", ["client_port=", "client_file_port=", "tracker_ip=", "tracker_port="]
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
            print(pad("-f"), "set client file transfer port")
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
