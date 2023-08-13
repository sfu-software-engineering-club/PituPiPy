from enum import Enum
import threading
import socket
import json
import os

CHUNK_SIZE = 4

class ServerMode(Enum):
    RECEIVER = (1,)
    SENDER = 2


class File:
    def __init__(self):
        self.identifier = None
        self.filepath = ""
        self.file_size = 0
        self.number_of_chunks = 0
        self.CHUNK_SIZE = CHUNK_SIZE

    def read_file(self, file_path):
        self.filepath = file_path
        
        with open(file_path, "rb") as file:
            chunk_count = 0
            while True:
                chunk = file.read(self.CHUNK_SIZE)
                if not chunk:
                    break
                chunk_count += 1
        self.file_size = chunk_count * self.CHUNK_SIZE
        self.number_of_chunks = chunk_count


class FileServer:
    def __init__(self, mode: ServerMode, file_info: File, ip_addr, port):
        self.mode = mode
        self.file_info = file_info
        self.ip_addr = ip_addr
        self.port = port
        self.mutex = threading.Lock()
        
    def send_file(self, receiver_ip_addr, receiver_port, chunk_start, chunk_end):
        transfer_thread = threading.Thread(target=self._send_file_transfer,
                                           args=(receiver_ip_addr, receiver_port, chunk_start, chunk_end))
        transfer_thread.start()

    def _send_file_transfer(self, receiver_ip_addr, receiver_port, chunk_start, chunk_end):
        data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        data_sock.connect((receiver_ip_addr, receiver_port))

        try:
            with open(self.file_info.filepath, "rb") as file:
                for chunk_index in range(chunk_start, chunk_end):
                    file.seek(chunk_index * self.file_info.CHUNK_SIZE)

                    chunk_data = file.read(self.file_info.CHUNK_SIZE)

                    with self.mutex:
                        data_sock.sendall(chunk_data)

        finally:
            data_sock.close()

    def inform_tracker(self, tracker_ip, tracker_port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((tracker_ip, tracker_port))

        sock.send(self.file_info.identifier)



    def request_file(
        self, destination_filepath, chunk_start, chunk_end
    ):
        transfer_thread = threading.Thread(target=self._request_file_transfer,
                                           args=(destination_filepath, chunk_start, chunk_end))
        transfer_thread.start()

    def _request_file_transfer(
            self, destination_filepath, chunk_start, chunk_end
    ):
        data_listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        data_listener.bind((self.ip_addr, self.port))
        data_listener.listen()

        data_sock, _ = data_listener.accept()

        try:
            """
            sock.connect((sender_ip_addr, sender_port))

            request = {
                "file_identifier": file_identifier,
                "chunk_start": chunk_start,
                "chunk_end": chunk_end,
                "receiver_ip_addr": sender_ip_addr,
                "receiver_port": sender_port
            }
            request_json = json.dumps(request)
            sock.sendall(request_json.encode())
            """
            file_offset = chunk_start * self.file_info.CHUNK_SIZE

            with open(destination_filepath, "w+b") as requested_file:
                requested_file.seek(file_offset)
                
                while True:
                    chunk_data = data_sock.recv(self.file_info.CHUNK_SIZE)
                    if not chunk_data:
                        break

                    with self.mutex:
                        requested_file.write(chunk_data)
        finally:
            data_sock.close()
            data_listener.close()


if __name__ == "__main__":

    # Get the current script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Get the parent directory
    parent_dir = os.path.dirname(script_dir)

    # Set the filename and file path
    filename = "sender_test_file.txt"
    sending_path = os.path.join(script_dir, filename)
    destination_filename = "receiver_test_file.txt"
    destination_path =  os.path.join(parent_dir, destination_filename)

     # Create file info object
    file = File()
    file.read_file(sending_path)

   # Create sender and receiver instances
    sender = FileServer(ServerMode.SENDER, file, "172.29.146.44", 4001)  
    receiver = FileServer(ServerMode.RECEIVER, file, "172.29.146.44", 4001)  

    # Requesting file from sender by receiver
    receiver.request_file(destination_path, 1, 6)
    
    # Sending file from sender to receiver
    sender.send_file(receiver.ip_addr, receiver.port, 1, 6)