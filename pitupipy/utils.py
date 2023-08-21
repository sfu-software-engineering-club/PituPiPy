import json
import socket


def local_ip_address():
    return socket.gethostbyname(socket.gethostname())


def json_encode(json_data):
    return json.dumps(json_data).encode()


def json_decode(byte_data):
    return json.loads(byte_data.decode("utf-8"))
