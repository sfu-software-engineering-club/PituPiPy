import sys
import getopt
import socket
from .tracker_api import TrackerApi


class TrackerProfile:
    def __init__(self, host, port, network_capacity=20) -> None:
        self.host = host
        self.port = port
        assert type(network_capacity) is int
        self.network_capacity = network_capacity

    def get_host_and_port(self):
        return (self.host, int(self.port))

    def get_network_capacity(self):
        return self.network_capacity


class Tracker:
    def __init__(self, port, capacity=20):
        self.profile = TrackerProfile(
            socket.gethostbyname(socket.gethostname()), port, capacity
        )
        self.api = TrackerApi(self.profile)

    def show_intro(self):
        print("  Python P2P Chat and File Transfer")
        print("  ")
        print("  Starting P2P Network Tracker\n")
        ip, port = self.profile.get_host_and_port()
        capacity = self.profile.get_network_capacity()
        print("HOST: {}".format(ip))
        print("PORT: {}".format(port))
        print("NETWORK CAPACITY: {}".format(capacity))

    def start(self):
        self.show_intro()
        self.api.run_on_terminal()


if __name__ == "__main__":
    argv = sys.argv[1:]
    opts, args = getopt.getopt(argv, "h", ["port="])

    port = None

    def pad(str):
        return str.ljust(15)

    tracker_params = []
    for opt, arg in opts:
        if opt == "-h":
            print(pad("--port"), "tracker port number")
            print("e.g. python tracker.py --port=3000")
            sys.exit()
        if opt == "--port":
            if len(args) != 0:
                port = int(arg)
                capacity = int(args[0])
                tracker_params = [port, capacity]
            else:
                port = int(arg)
                tracker_params = [port]
    if None in tracker_params:
        print("Error: Missing command argument")
        sys.exit()

    tracker = Tracker(*tracker_params)
    tracker.start()
