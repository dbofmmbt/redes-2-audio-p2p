import contextlib
import json
import socket

import pytest


@contextlib.contextmanager
def client_conn():
    with socket.socket() as s:
        s.connect(("localhost", 8080))
        yield s


def check(payload: dict, expected: dict):
    serialized = json.dumps(payload)

    with client_conn() as s:
        s.sendall(serialized.encode())
        response = s.recv(4096)
        assert json.loads(response) == expected


def test_hello_world():
    check(payload={"action": "health"}, expected={"message": "OK"})


def test_register():
    check(
        payload={"action": "register", "songs": ["song1"]}, expected={"message": "OK"}
    )


def test_unregister():
    check(payload={"action": "unregister"}, expected={"message": "OK"})


