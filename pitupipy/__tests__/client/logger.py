import sys
import os


class Logger:
    def __init__(self, location):
        self.location = location

    def create_log_file(self):
        self.location = self.location.strip('"')
        os.makedirs(os.path.dirname(self.location), exist_ok=True)
        print(f"Saving log file at : [{self.location}]")

    def log_message(self, message):
        with open(self.location, "a") as f:
            f.write(f"Sending message : [{message}]\n")
