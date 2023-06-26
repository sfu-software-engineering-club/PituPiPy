class CLI:
    COMMAND_PROMPT = "\nCOMMAND? [/q or /shutdown] >> /"

    def __init__(self, client):
        self.client = client

    def cli(self):
        self.client.print_help()
        while True:
            print("\n")
            print(self.COMMAND_PROMPT, end="")
            cmd = input()
            message = ""

            if len(cmd.split(" ", 1)) > 1:
                cmd, message = cmd.split(" ", 1)
            else:
                cmd = cmd.strip()

            try:
                if cmd == "help":
                    self.client.print_help()

                elif cmd == "connect":
                    self.client.connect_to_tracker()

                elif cmd == "status":
                    peer_list = self.client.request_tracker_list_of_peers()
                    
                elif cmd == "send_message":
                    if self.client.node is None:
                        raise Exception("Error: client is not connected to network")
                    elif message == "":
                        print("No message provided")
                    else:
                        print("Sending message: [{}]".format(message))
                        self.client.node.broadcast_message(message)

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
