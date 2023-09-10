import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import socket
import threading
import uuid
import json
import traceback
from client.file_server.file_server import File

class Network:
    def __init__(self, network_capacity=20) -> None:
        assert type(network_capacity) is int
        self.capacity = network_capacity
        self.client_connections = []

    def get_network_capacity(self):
        return self.capacity

    def add_client_connection_to_network(self, client_connection):
        assert len(self.client_connections) < self.capacity
        self.client_connections.append(client_connection)
        print(
            "Network participants: ", len(self.client_connections), " / ", self.capacity
        )

    def remove_client_from_network(self, client_connection):
        pass

    def client_join_attempt(self, client_connection):
        """
        Return True and add a client to the network if a network can accept a new client
        Return None if not
        """
        cli_nums = len(self.client_connections)
        if cli_nums < self.capacity:
            self.add_client_connection_to_network(client_connection)
            return True
        else:
            return False

    def get_all_client_connections(self):
        return self.client_connections

    def get_client_connection_by_id(self, client_id):
        for c in self.client_connections:
            id = c.get_client_id()
            if id is client_id:
                return c
        return None

    def is_client_in_network(self, client_id):
        if self.get_client_connection_by_id(client_id):
            return True
        return False


class ClientConnection(threading.Thread):
    def __init__(self, network, client_socket, host, port, file_manager):
        super(ClientConnection, self).__init__()
        self.network = network
        self.client_connection_socket = client_socket
        self.client_name = None
        self.client_ip = host
        self.client_port = port
        self.client_id = str(uuid.uuid4())
        self.stop_flag = False
        self.file_manager = file_manager

    def get_host_and_port(self):
        return (self.client_ip, int(self.client_port))

    def get_client_id(self):
        return self.client_id

    def send_message(self, api_key, message, status=200):
        """Send a message to client"""
        assert api_key is not None
        data = {
            "api_key": api_key,
            "status_code": status,
            "value": message,
        }
        self.client_connection_socket.send(json.dumps(data).encode())
        return data

    def send_error_message(self, api_key, error_message, error_code=500):
        assert api_key is not None
        data = {
            "api_key": api_key,
            "status_code": str(error_code),
            "value": error_message,
        }
        self.client_connection_socket.send(json.dumps(data).encode())
        return data

    def send_invalid_request(self):
        return self.send_error_message(
            api_key="INVALID_REQUEST", error_message="Malformed client request"
        )

    def send_server_error(self):
        return self.send_error_message(
            api_key="SERVER_ERROR",
            error_message="Unknown error occured",
            error_code=500,
        )

    def receive_message(self):
        res = self.client_connection_socket.recv(1024).decode("utf-8")
        return json.loads(res)

    def peer_list(self):
        peer_list = []
        for p in self.network.get_all_client_connections():
            host, port = p.get_host_and_port()
            client_id = p.get_client_id()
            client_name = p.client_name
            peer_list.append(
                {
                    "id": client_id,
                    "name": client_name,
                    "ip": host,
                    "port": port,
                }
            )
        return peer_list
    
    def transform_file_list_id_to_name(self, id_file_list):
        peer_list = self.peer_list()
        id_to_name = {peer['id']: peer['name'] for peer in peer_list}
    
        name_file_list = []
        for file_info in id_file_list:
            transformed_owners = [id_to_name[owner_id] for owner_id in file_info['owners']]
            transformed_info = {
                "id": file_info["id"],
                "owners": transformed_owners,
            }
            name_file_list.append(transformed_info)
        
        return name_file_list
    
    def close(self):
        self.client_connection_socket.close()
        self.stop_flag = True

    def run(self):
        while not self.stop_flag:
            received = self.receive_message()
            print("\nData received: ", received)
            try:
                assert "api_key" in received
            except Exception as e:
                self.send_invalid_request()
            try:
                api_key = received["api_key"]
                value = received["value"] if "value" in received else None
                response = None

                if api_key == "CONNECT":
                    self.client_id = str(uuid.uuid4())
                    self.client_name = value["name"]
                    self.client_ip = value["ip"]
                    self.client_port = value["port"]
                    # To avoid TCP outgoing port selection
                    success = self.network.client_join_attempt(self)
                    if not success:
                        response = self.send_error_message(
                            api_key="CONNECT", error_message="Network is full"
                        )
                    else:
                        response = self.send_message(
                            api_key="CONNECT",
                            message={
                                "network_name": "myNet",
                                "client_id": self.get_client_id(),
                            },
                        )

                elif api_key == "LIST_PEERS":
                    peer_list = self.peer_list()
                    response = self.send_message(
                        api_key="LIST_PEERS", message=peer_list
                    )

                elif api_key == "HEALTH_CHECK":
                    response = self.send_message(api_key="HEALTH_CHECK", message="ok")

                elif api_key == "FILE_UPLOAD":
                    file_path = value["path"]
                    file_size = value["size"]
                    file_chunks = value["chunks"]
                    owner_id = value["owner"]
                    file_id = self.file_manager.upload_new_file(file_path, file_size, file_chunks, owner_id)
                    response = self.send_message(
                        api_key="FILE_UPLOAD", 
                        message={
                            "file_id": file_id
                        },
                    )
                
                elif api_key == "FILE_LIST":
                    id_file_list = self.file_manager.get_file_list()
                    name_file_list = self.transform_file_list_id_to_name(id_file_list)
                    response = self.send_message(
                        api_key="FILE_LIST", message=name_file_list
                    )

                elif api_key == "QUIT":
                    self.network.remove_client_from_network(self)
                    response = self.send_message(api_key="QUIT", message="ok")

                else:
                    self.send_invalid_request()

                print("Response: ", response)

            except Exception as e:
                self.send_server_error()
                traceback.print_exc()
                return

class FileManager:
    def __init__(self):
        self.file_info = {}

    def upload_new_file(self, file_path, file_size, chunks, owner_id):
        new_file = File()
        new_file.filepath = file_path
        new_file.file_size = file_size
        new_file.number_of_chunks = chunks
        new_file.add_owner(owner_id)
        file_id = str(uuid.uuid4())
        new_file.identifier = file_id

        self.file_info[file_id] = new_file
        return file_id

    def get_file_info(self, file_id):
        return self.file_info.get(file_id, None)
    
    def get_file_list(self):
        file_list = []
        for file_id, file_instance in self.file_info.items():
            owners = file_instance.get_owners()
            file_info = {
                "id": file_id,
                "owners": owners,
            }
            file_list.append(file_info)
        return file_list


class TrackerApi:
    def __init__(self, profile):
        assert profile is not None

        self.profile = profile
        self.network = Network(profile.get_network_capacity())
        self.server_socket = self.create_server_socket()
        self.client_connections = []
        self.file_manager = FileManager()

    def create_server_socket(self):
        ip, port = self.profile.get_host_and_port()
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((ip, port))
        server_socket.listen()
        self.server_socket = server_socket
        return server_socket

    def run_on_terminal(self):
        print("\nTracker API Listening")
        while True:
            client_socket, address = self.server_socket.accept()
            host, port = address
            print("\nNew connection request received: ", host, ":", port)
            connection = self.create_new_client_connection(client_socket, host)
            self.client_connections.append(connection)

    def create_new_client_connection(self, client_socket, host, port=None):
        client_connection = ClientConnection(
            self.network, client_socket, host, port=None, file_manager=self.file_manager
        )
        client_connection.daemon = True
        client_connection.start()
        return client_connection

    def __del__(self):
        for c in self.client_connections:
            c.close()
        self.server_socket.close()
