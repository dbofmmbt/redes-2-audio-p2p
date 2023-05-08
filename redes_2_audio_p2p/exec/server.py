from contextlib import suppress
import json
import os
import signal
import socket
import threading
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("server")


def send(conn: socket.socket, payload: dict):
    conn.sendall(json.dumps(payload).encode())


def handle(conn: socket.socket, addr):
    with conn:
        request_bytes = conn.recv(4096)
        if not request_bytes:
            return
        request = json.loads(request_bytes)
        match request.get("action"):
            case "register":
                logger.info(f"registering user {addr}")
                send(conn, {"message": "TODO"})
            case "unregister":
                logger.info(f"unregistering user {addr}")
                send(conn, {"message": "TODO"})
            case "health":
                logger.info("sending OK")
                send(conn, {"message": "OK"})
            case invalid:
                logger.error(f"invalid action {invalid}")


stop_server = False


def server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # When running tests, we want to reuse sockets.
    # https://stackoverflow.com/questions/337115/setting-time-wait-tcp
    if os.environ.get("TEST"):
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    s.bind(("localhost", 8080))
    s.settimeout(0.1)
    s.listen()

    logger.info("ready to receive connections")

    while not stop_server:
        with suppress(TimeoutError):
            conn, addr = s.accept()
            logger.info("received connection")
            threading.Thread(target=handle, args=(conn, addr)).run()

    logger.info("stopping server")
    s.close()


def stop(sig, frame):
    global stop_server
    stop_server = True


signal.signal(signal.SIGINT, stop)

server()
