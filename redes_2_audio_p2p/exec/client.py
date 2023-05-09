import logging
import contextlib
import json
import socket

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("client")

logger.info("TODO client")

my_id = -1
my_songs = []

@contextlib.contextmanager
def client_conn():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(("localhost", 8080))
        yield s



stop_connection = False
def start_client():

    with client_conn() as s:

        #first message received is info (necessary?)
        read_info_message(s)
        
        #second message received is confirmation
        read_confirmation_message(s)

        while not stop_connection:
            x = 1   # O que a gnt faz aqui? n tem que terminar conexão mas tbm não mais o que receber


def send_message(s: socket, payload: dict):
    serialized = json.dumps(payload)
    s.sendall(serialized.encode())
    

def fill_dummy_songs():
    for i in range(3):
        my_songs.append(f"song{i + my_id*3}")

def send_register_message(s):
    message = {"action": "register", "songs": my_songs}
    send_message(s, message)

def read_confirmation_message(s):
    request_bytes = s.recv(4096)
    if not request_bytes:
        return

    request = json.loads(request_bytes)
    
    match request.get("message"):
        case "OK":
            logger.info("OK")

        case "Not OK":
            logger.info("Not OK")

def read_info_message(s):
    request_bytes = s.recv(4096)
    if not request_bytes:
        return
    
    request = json.loads(request_bytes)

    if("info" in request):
        my_id = int(request.get("info"))
        fill_dummy_songs()
        send_register_message(s)
    

start_client()