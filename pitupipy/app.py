from client.client import Client


if __name__ == "__main__":
    client = Client()
    client.listen(3001)

    """
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
    """
