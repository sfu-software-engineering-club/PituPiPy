import os
import sys


class CLI:
    COMMAND_PROMPT = "\nCOMMAND? [/q or /shutdown] >> /"

    def __init__(self, client, log_file):
        self.client = client
        self.log_file = log_file

    def print_help(self):
        def format(str1, str2):
            return "{:<20} {}".format(str1, str2)

        self.log_file.write_log_message(format("Options", "") + "\n")
        self.log_file.write_log_message(
            format("/connect", "-- connect to tracker\n"))
        self.log_file.write_log_message(
            format("/status", "-- show the current network connection status\n"))
        self.log_file.write_log_message(
            format("/send_message [message]", "-- send a message to network\n"))
        self.log_file.write_log_message(
            format("/exit", "-- exit from network\n"))
        self.log_file.write_log_message(
            format("/shutdown", "-- terminate the client\n\n"))

    def write_terminal(self):
        # clear terminal screen before printing COMMAND_PROMPT
        # Windows : cls
        # Unix : clear
        os.system("cls" if os.name == "nt" else "clear")

        self.log_file.show_log_message()

    def run_on_terminal(self):
        self.print_help()

        while True:
            self.write_terminal()

            # get terminal size
            term_rows, term_cols = os.get_terminal_size()

            # calculate number of lines needed to print
            num_lines_needed = (len(self.COMMAND_PROMPT) +
                                term_cols - 1) // term_cols

            # move cursor to last line to print COMMAND_PROMPT
            print("\033[{};0H".format(term_rows - num_lines_needed))

            print(self.COMMAND_PROMPT, end="")

            cmd = input()
            message = ""

            if len(cmd.split(" ", 1)) > 1:
                cmd, message = cmd.split(" ", 1)
            else:
                cmd = cmd.strip()

            try:
                if cmd == "help":
                    self.print_help()

                elif cmd == "connect":
                    self.client.connect_to_tracker()

                elif cmd == "status":
                    peer_list = self.client.request_tracker_list_of_peers()

                elif cmd == "send_message":
                    if self.client.client_connection_node is None:
                        raise Exception(
                            "Error: client is not connected to network")
                    elif message == "":
                        self.log_file.write_log_message("No message provided")
                        self.write_terminal()

                    else:
                        self.client.client_connection_node.broadcast_message(
                            message)
                        if self.log_file is not None:
                            self.log_file.write_log_message(
                                "\nMessage Sent: {}\n".format(message))
                            self.write_terminal()

                elif cmd == "exit":
                    success = self.client.request_tracker_exit_network()
                    if success:
                        print("Successfully exited from network")
                    else:
                        print("Error: Failed to exit from network")

                elif cmd == "/q" or cmd == "shutdown":
                    self.client.shutdown()
                    sys.exit()

                else:
                    print("Error: unknown command: {}".format(cmd))
            except Exception as e:
                print(e)
