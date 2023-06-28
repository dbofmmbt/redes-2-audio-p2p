import glob
import logging
import contextlib
import json
import socket
import wave
from .wave_receiver import run_audio_receiver
from .wave_sender import run_audio_sender

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("client")

server_ip = "localhost"
server_port = 8080

my_p2p_port = 0000
songs_files_dir = "songs/"
all_songs_paths = []

known_clients = []

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
            print("4 - request song from client")
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

                case 4:
                    client_index, song_index = get_song_input()
                    send_request_song(s, client_index, song_index)
                    request_confirmed = read_confirmation_message(s)
                    
                    if(request_confirmed):
                        start_wave_receiver()
                    else:
                        print("Client no longer available")
                        

def start_wave_receiver():
    run_audio_receiver(my_p2p_port)


def send_request_song(s, client_index, song_index):

    client = known_clients[client_index]
    message = {"action": "notify-request", "client": {"ip": client.get("ip"), "port": client.get("port")}, "song": known_clients[client_index].get("songs")[song_index]}
    logger.info("sending message: ")
    logger.info(message)
    logger.info("")
    send_message(s, message)
    logger.info("request_song message sent")
    
def get_song_input():
    
    for i in range(len(known_clients)):
        print(f"Client {i}: ", end="")
        print(known_clients[i])
    
    client_index = int(input("Input a client number: "))

    print(f"Client {client_index} musics: ")
    for i in range(len(list(known_clients[client_index].values()))):
        print(f"Song {i}: {known_clients[client_index].get('songs')[i]}")

    song_index = int(input("Input a song number: "))
    return (client_index, song_index)


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
            return True

        case "Not OK":
            logger.info("Not OK")
            return False
        
        
    return True


def read_list_message(s):
    request_bytes = s.recv(4096)
    if not request_bytes:
        return

    request = json.loads(request_bytes)
    logger.info("Received clients songs list message")

    global known_clients
    known_clients = request.get("peers")

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
    my_p2p_port = int(input("Type the client port: "))

    global songs_files_dir, all_songs_paths
    songs_files_dir = input("Type client's folder name: (\"example/\"): ")
    all_songs_paths = get_songs_paths()
    print(f"all_songs_paths: {all_songs_paths}")

    send_register_message(s, my_p2p_port, get_songs_names())
    request_bytes = s.recv(4096)
    with separator():
        print(json.loads(request_bytes))


start_client()
