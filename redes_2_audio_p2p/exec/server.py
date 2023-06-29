from contextlib import suppress
import json
import os
import signal
import socket
import threading
import logging
from redes_2_audio_p2p import handler

from ..handler import health_handler, list_handler, register_handler, unregister_handler, notify_request_handler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("server")

all_cons = []

def handle(conn: socket.socket, addr):
    with conn:
        try:
            while request_bytes := conn.recv(4096):
                request = json.loads(request_bytes)

                match request.get("action"):
                    case "register":
                        register_handler(conn, addr, request)
                    case "unregister":
                        unregister_handler(conn, addr, request)
                    case "list":
                        list_handler(conn, addr, request)
                    case "health":
                        health_handler(conn, addr, request)
                    case "notify-request":
                        notify_request_logic(conn, addr, request)
                    case invalid:
                        logger.error(f"invalid action {invalid}")
        finally:
            logger.info(f"disconnecting {addr}")
            if addr in handler.peers:
                handler.unregister_songs(addr)


stop_server = False

def notify_request_logic(conn, addr, request):
    
    target_client_addr = (request.get("client").get("ip"), request.get("client").get("port"))

    for i in range(len(all_cons)):
        if(all_cons[i].getpeername() == target_client_addr):
                print("Igualllll")
                target_conn = all_cons[i]
        
    notify_request_handler(conn, addr, request, target_conn)


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
            threading.Thread(target=handle, args=(conn, addr)).start()


    logger.info("stopping server")
    s.close()


def stop(sig, frame):
    global stop_server
    stop_server = True


signal.signal(signal.SIGINT, stop)

server()
