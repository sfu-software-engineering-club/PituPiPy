from enum import Enum
from chunk import Chunk
import threading
import socket
import json


class ServerMode(enum):
    RECEIVER = (1,)
    SENDER = 2


class File:
    def __init__(self):
        self.identifier = None
        self.filepath = ""
        self.file_size = 0
        self.number_of_chunks = 0


class FileServer:
    def __init__(self, mode: ServerMode, file_info: File, ip_addr, port):
        self.mode = mode
        self.file_info = file_info
        self.ip_addr = ip_addr
        self.port = port
        self.mutex = threading.Lock()
        pass

    def send_file(self, receiver_ip_addr, receiver_port, chunk_start, chunk_end):
        # if len(offsets) == 1:  # chunk end (exclusive)
        #    pass
        # if len(offsets) == 2:  # chunk start, chunk end
        #    pass

        # Create a new thread for the file transfer
        transfer_thread = threading.Thread(
            target=self._send_file_transfer,
            args=(receiver_ip_addr, receiver_port, chunk_start, chunk_end),
        )
        transfer_thread.start()

    def _send_file_transfer(
        self, receiver_ip_addr, receiver_port, chunk_start, chunk_end
    ):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((receiver_ip_addr, receiver_port))

        try:
            # Read and send the specified chunks
            with open(
                self.file_info.filepath, "rb"
            ) as file:  # 'rb' -> reading in Binary mode
                chunk = Chunk(file, True, True, False)
                for chunk_index in range(chunk_start, chunk_end):
                    # Seek to the start of the current chunk
                    chunk.seek(chunk_index)

                    # Read the chunk from the file
                    chunk_data = chunk.read()

                    # Send the chunk to the receiver
                    with self.mutex:
                        sock.sendall(chunk.getsize())
                        sock.sendall(chunk_data)
        finally:
            # Close the socket
            sock.close()

    def request_file(
        self,
        destination_filepath,
        sender_ip_addr,
        sender_port,
        chunk_start,
        chunk_end,
        file_identifier,
    ):
        transfer_thread = threading.Thread(
            target=_request_file_transfer,
            args=(
                destination_filepath,
                sender_ip_addr,
                sender_port,
                chunk_start,
                chunk_end,
                file_identifier,
            ),
        )
        transfer_thread.start()

    def _request_file_transfer(
        destination_filepath,
        sender_ip_addr,
        sender_port,
        chunk_start,
        chunk_end,
        file_identifier,
    ):
        # Open a socket connection to the sender
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to the sender's IP address and port
            sock.connect((sender_ip_addr, sender_port))

            # Send the file request to the sender
            request = {
                "file_identifier": file_identifier,
                "chunk_start": chunk_start,
                "chunk_end": chunk_end,
                "receiver_ip_addr": sender_ip_addr,
                "receiver_port": sender_port,
            }
            request_json = json.dumps(request)
            sock.sendall(request_json.encode())

        # Create/open the destination file to write the received data
        file_offset = chunk_start * 4

        with open(
            destination_filepath, "r+b"
        ) as requested_file:  # reading & writing in Binary mode
            # Seek to the correct position in the file based on the file offset
            requested_file.seek(file_offset)
            # Receive and write the requested chunks to the destination file
            while True:
                chunk_size_byte = sock.recv(4)
                if not chunk_size_byte:
                    break
                chunk_size = int.from_bytes(chunk_size_byte, byteorder="big")

                chunk_data = sock.recv(chunk_size)
                if not chunk_data:
                    break
                with self.mutex:
                    requested_file.write(chunk_data)


if __name__ == "__main__":
    pass
