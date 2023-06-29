import sys
import getopt
import socket
from tracker_api import TrackerApi


class Tracker:
    def __init__(self, port, capacity=20):
        self.hostname = socket.gethostname()
        self.ip = socket.gethostbyname(self.hostname)
        self.port = port
        self.capacity = capacity
        self.api = TrackerApi(self.ip, self.port, self.capacity)

    def start(self):
        print("  Python P2P Chat and File Transfer")
        print("  ")
        print("  Starting P2P Network Tracker\n")

        print("HOST: {}".format(self.ip))
        print("PORT: {}".format(self.port))

        self.api.start()


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
