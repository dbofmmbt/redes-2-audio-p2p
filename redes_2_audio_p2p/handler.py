import json
import logging
import socket

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

peers = {}


def send(conn: socket.socket, payload: dict):
    conn.sendall(json.dumps(payload).encode())


def register_handler(conn, addr, request):
    logger.info(f"registering user {addr}")
    if addr not in peers:
        register_songs(addr, request)
        send(conn, {"message": "user registered succesfully"})
    else:
        send(conn, {"message": "user already exists"})


def register_songs(addr, request):
    peers[addr] = {"ip": addr[0], "port": request["port"], "songs": request["songs"]}


def unregister_handler(conn, addr, request):
    logger.info(f"unregistering user {addr}")
    unregister_songs(addr)
    send(conn, {"message": "OK"})


def unregister_songs(addr):
    try:
        peers.pop(addr)
    except:
        logger.error(
            "Connection not in dictionary... Trying to unregister client that was never registered"
        )


def list_handler(conn, addr, request):
    logger.info(f"Listing songs to user {addr}")
    send(conn, {"peers": list(peers.values())})


def health_handler(conn, addr, request):
    logger.info("sending OK")
    send(conn, {"message": "OK"})
