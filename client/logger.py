import os
import uuid


class Logger:
    def __init__(self):
        # generate unique client ID using UUID
        self.client_id = str(uuid.uuid4())

        # create "logger" folder
        log_folder = os.path.join(os.getcwd(), "logger")
        os.makedirs(log_folder, exist_ok=True)

        self.location = os.path.join(
            log_folder, f"{self.client_id}.txt")

    def write_log_message(self, message):
        print(message)
        with open(self.location, "a") as f:
            f.write(message)

    def show_log_message(self):
        try:
            with open(self.location, "r") as f:
                log_messages = f.read()
                print(log_messages)
        except FileNotFoundError:
            print(f"Log file for client {self.client_id} not found.")
        except Exception as e:
            print(f"An error occured while reading log file: {e}")

    def delete_log_file(self):
        try:
            os.remove(self.location)
            print("Log file is deleted.\n")
        except FileNotFoundError:
            print(f"Log file for client {self.client_id} not found.")
        except Exception as e:
            print(f"An error occured while deleting log file: {e}")
