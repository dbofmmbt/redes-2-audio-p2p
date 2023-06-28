import json
import logging
import socket

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

peers = {}
test_list = []


def send(conn: socket.socket, payload: dict):
    conn.sendall(json.dumps(payload).encode())
    test_list.append("a")

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
    logger.info(f"Listing songs to user {addr} {list(peers.values())}")
    send(conn, {"peers": list(peers.values())})


def health_handler(conn, addr, request):
    logger.info("sending OK")
    send(conn, {"message": "OK"})

def notify_request_handler(conn, addr, request):

    target_client_addr = (request.get("client").get("ip"), request.get("client").get("port"))

    print(f"Target_addr: {target_client_addr}")
    print(peers)

    peers_values = list(peers.values())
    for i in range(len(peers_values)):

        ip, port = target_client_addr
        if peers_values[i].get("ip") == ip and peers_values[i].get("port") == port :
            print("Found it!")
            send(conn, {"message": "OK"})
        else:
            send(conn, {"message": "Not OK"})

    