class CLI:
    def __init__(self, client):
        self.client = client

    def cli(self):
        COMMAND_PROMPT = "\nCOMMAND? [/q or /shutdown] >> /"
        self.client.print_help()
        while True:
            print("\n")
            print(COMMAND_PROMPT, end="")
            cmd = str(input())

            try:
                if cmd == "help":
                    self.client.print_help()

                elif cmd == "connect":
                    self.client.connect_to_tracker()

                elif cmd == "status":
                    peer_list = self.client.request_tracker_list_of_peers()
                    for id, ipAddr in peer_list:
                        print("[ID: {}] {}".format(id, ipAddr))

                elif cmd == "send_message":
                    # TODO
                    # print("sending message: [{}]".format(message))
                    # self.client.send_message_to_network(message)
                    pass

                elif cmd == "exit":
                    success = self.client.request_tracker_exit_network()
                    if success:
                        print("Successfully exited from network")
                    else:
                        print("Error: Failed to exit from network")

                elif cmd == "/q" or cmd == "shutdown":
                    self.client.shutdown()

                else:
                    print("Error: unknown command: {}".format(cmd))
            except Exception as e:
                print(e)
