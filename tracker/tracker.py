import sys
import getopt
import socket
from network import TrackerNode


class Tracker:
    def __init__(self, port):
        self.hostname = socket.gethostname()
        self.ip = socket.gethostbyname(self.hostname)
        self.port = port

        self.socket = None
        self.node = None

    def start(self):
        print("  Python P2P Chat and File Transfer")
        print("  ")
        print("  Starting P2P Network Tracker\n")

        print("HOST: {}".format(self.ip))
        print("PORT: {}".format(self.port))

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.ip, self.port))
        self.socket.listen()

        self.node = TrackerNode(self.socket, self.ip, self.port)
        self.node.daemon = True
        self.node.start()

        self.cli()

    def print_help(self):
        def pad(str):
            return str.ljust(20)

        print("\n")
        print(pad("  Options"))
        print(pad("/list_peers"), "--", "list all the peer IPs in the network")
        print(pad("/shutdown"), "--", "terminate the tracker")

    def shutdown():
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

            elif cmd == "list_peers":
                pass

            elif cmd == "/q" or cmd == "shutdown":
                self.shutdown()

            else:
                print("Error: unknown command: {}".format(cmd))


if __name__ == "__main__":
    argv = sys.argv[1:]
    opts, args = getopt.getopt(argv, "h", ["port="])

    port = None

    def pad(str):
        return str.ljust(15)

    for opt, arg in opts:
        if opt == "-h":
            print(pad("--port"), "tracker port number")
            print("e.g. python tracker.py --port=3000")
            sys.exit()
        if opt == "--port":
            port = arg

    tracker_params = [port]

    if None in tracker_params:
        print("Error: Missing command argument")
        sys.exit()

    tracker = Tracker(*tracker_params)
    tracker.start()
