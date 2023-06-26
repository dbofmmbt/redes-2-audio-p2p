import glob
import logging
import contextlib
import json
import socket

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("client")

server_ip = "localhost"
server_port = 8080

songs_files_dir = "songs/"
all_songs_paths = []



@contextlib.contextmanager
def client_conn():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((server_ip, server_port))
        logger.info(f"Connected with {server_ip} in port {server_port}")
        yield s


stop_connection = False


def start_client():


    with client_conn() as s:
        while not stop_connection:
            print("What is the next action?")
            print("1 - register")
            print("2 - Unregister")
            print("3 - list clients songs")
            print("0 - quit")
            next_action = int(input("Type the corresponding number: "))

            match next_action:
                case 0:
                    return
                case 1:
                    register_behaviour(s)

                case 2:
                    send_unregister_message(s)
                    read_confirmation_message(s)

                case 3:
                    send_list_message(s)
                    read_list_message(s)


def send_message(s: socket, payload: dict):
    serialized = json.dumps(payload)
    s.sendall(serialized.encode())


def send_register_message(s, port, songs):
    message = {"action": "register", "port": port, "songs": songs}
    send_message(s, message)
    logger.info("Register message sent")


def send_unregister_message(s):
    message = {"action": "unregister"}
    send_message(s, message)
    logger.info("Unregister message sent")


def send_list_message(s):
    message = {"action": "list"}
    send_message(s, message)
    logger.info("List message sent")


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


def read_list_message(s):
    request_bytes = s.recv(4096)
    if not request_bytes:
        return

    request = json.loads(request_bytes)
    logger.info("Received clients songs list message")

    with separator():
        print(request)


@contextlib.contextmanager
def separator():
    print("*****************************")
    yield
    print("*****************************")


def get_songs_paths():
    print(f"Looking for files in {songs_files_dir}")
    path = "songs/" + songs_files_dir + "*.wav"
    return  glob.glob(path)

def get_songs_names():
    songs_names = []
    for song_path in all_songs_paths:
        songs_names.append(song_path.split('/')[-1])

    return songs_names

def register_behaviour(s):
    port = int(input("Type the client port: "))

    global songs_files_dir, all_songs_paths
    songs_files_dir = input("Type client's folder name: (\"example/\"): ")
    all_songs_paths = get_songs_paths()
    print(f"all_songs_paths: {all_songs_paths}")

    send_register_message(s, port, get_songs_names())
    request_bytes = s.recv(4096)
    with separator():
        print(json.loads(request_bytes))

all_songs_paths = get_songs_paths()

start_client()
