import socket

from tenhou.client import TenhouClient

HOST = '133.242.10.78'
PORT = 10080

def connect_and_play():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))

    client = TenhouClient(s)
    was_auth = client.authenticate()

    if was_auth:
        client.start_the_game()
    else:
        client.end_the_game()