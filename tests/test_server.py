import contextlib
import socket


@contextlib.contextmanager
def client_conn():
    with socket.socket() as s:
        s.connect(("localhost", 8080))
        yield s


def test_hello_world():
    with client_conn() as s:
        response = s.recv(100)
        assert response == b"OK"
