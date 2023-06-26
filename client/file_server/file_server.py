from enum import Enum
from chunk import Chunk


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
        self.file_path = ""
        pass

    def send_file(self, receiver_ip_addr, receiver_port, chunk_start, chunk_end):
        if len(offsets) == 1:  # chunk end (exclusive)
            pass
        if len(offsets) == 2:  # chunk start, chunk end
            pass

    def request_file(
        self, destination_filepath, sender_ip_addr, sender_port, chunk_start, chunk_end
    ):
        pass


if __name__ == "__main__":
    pass
