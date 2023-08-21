import json
import socket
import os


def local_ip_address():
    return socket.gethostbyname(socket.gethostname())


def json_encode(json_data):
    return json.dumps(json_data).encode()


def json_decode(byte_data):
    return json.loads(byte_data.decode("utf-8"))


def window_length():
    _, columns = os.popen("stty size", "r").read().split()
    return columns


def clear_window():
    os.system("cls" if os.name == "nt" else "clear")


def draw_line():
    w_len = window_length()
    print(("{0:─^" + w_len + "}").format(""))


def draw_empty():
    w_len = window_length()
    print(("{0:─^" + w_len + "}").format(""))


def draw_center_text(text):
    w_len = window_length()
    print("│" + ("{0:^" + str(int(w_len) - 2) + "}").format(text) + "│")


def draw_left_text(text):
    w_len = window_length()
    print(
        "│" + text + ("{0:^" + str(int(w_len) - 2 - len(text)) + "}").format("") + "│"
    )
