import contextlib
import json
import socket


def client_connect():
    s = socket.socket()
    s.connect(("localhost", 8080))
    return s


@contextlib.contextmanager
def client_conn():
    s = client_connect()
    yield s
    s.shutdown(socket.SHUT_WR)
    s.close()


def check(payload: dict, expected: dict):
    with client_conn() as s:
        response = send_request(s, payload)
        assert response == expected


def send_request(s, payload):
    serialized = json.dumps(payload)
    s.sendall(serialized.encode())
    response = s.recv(4096)
    return json.loads(response)
