import glob
import logging
import contextlib
import json
import select
import socket
import signal
import sys
import threading
import wave
from .globals import finish
from .wave_sender import run_audio_sender
from .wave_receiver import run_audio_receiver, frames

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("client")

server_ip = "localhost"
server_port = 8080

my_ip = "0.0.0.0"
my_p2p_port = 9898
songs_files_dir = "songs/"
all_songs_paths = []

known_clients = []



@contextlib.contextmanager
def client_conn():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((server_ip, server_port))
        #logger.info(f"Connected with {server_ip} in port {server_port}")
        yield s


stop_connection = False

@contextlib.contextmanager
def client_to_client_conn(server_ip, server_port):

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((server_ip, server_port))
        logger.info(f"Connected with another client: {server_ip} in port {server_port}")
        yield s


def start_client():

    with client_conn() as s:

        hostname=socket.gethostname()
        global my_ip
        my_ip = socket.gethostbyname(hostname)

        while not stop_connection:
            print("What is the next action?")
            print("1 - register")
            print("2 - Unregister")
            print("3 - list clients songs")
            print("4 - request song from client")
            print("5 - stop music")
            print("0 - quit")
            next_action = int(input("Type the corresponding number: "))

            match next_action:
                case 0:
                    stop(None, None)
                    return
                case 1:
                    register_behaviour(s)
                    threading.Thread(target=client_tcp).start()

                case 2:
                    send_unregister_message(s)
                    result = read_confirmation_message(s)
                    if(result):
                        global stop_server
                        stop_server = True
                case 3:
                    send_list_message(s)
                    read_list_message(s)
                    print_known_clients()

                case 4:
                    send_list_message(s)
                    read_list_message(s)
                    print();
                    client_index, song_index = get_song_input()
                    send_request_song(client_index, song_index)

                case 5:
                    finish["receive"] = True
                    

stop_server = False
def client_tcp():

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #logger.info(f"ip and port: {my_ip} {my_p2p_port}")
    s.bind(("0.0.0.0", my_p2p_port))
    s.settimeout(0.1)
    s.listen()

    global stop_server
    while not stop_server:
        with contextlib.suppress(TimeoutError):
            conn, addr = s.accept()
            #logger.info("received connection")
            threading.Thread(target=sender_control, args=(conn, addr)).start()
    
    stop_server = False
    logger.info("stopping p2p connection")
    s.close()


def sender_control(conn, addr):
    conn.settimeout(4)
    with conn:
        try:
            while True:
                
                try:
                    request_bytes = conn.recv(4096)
                    if not request_bytes:
                        continue
                    
                    request = json.loads(request_bytes)

                    
                    match request.get("action"):
                        case "notify-request":
                            send_message(conn, {"message": "OK"})
                            finish["send"] = False
                            handle_song_request(request)

                        case "stop":
                            finish["send"] = True

                except socket.timeout:
                    
                    if(finish["send"]):
                        send_message(conn, {"message": "DONE"} )
                        return

        finally:
            logger.info(f"disconnecting {addr}")
            
def handle_song_request(request):

    ip = request.get("client").get("ip")
    port = request.get("client").get("port")
    song = request.get("song")

    run_audio_sender(get_song_path(song), ip, port)

def stop(sig, frame):
    global stop_server, finish, finish_receive
    stop_server = True
    finish["send"] = True
    finish["receive"] = True



signal.signal(signal.SIGINT, stop)

def get_song_path(song):
    return "songs/" + songs_files_dir + song

def start_wave_receiver():
    threading.Thread(target=run_audio_receiver, args=(my_p2p_port+1,)).start()


def send_request_song(client_index, song_index):

    client = known_clients[client_index]
    message = {"action": "notify-request", "client": {"ip": my_ip, "port": my_p2p_port+1}, "song": known_clients[client_index].get("songs")[song_index]}
    
    with client_to_client_conn(client.get("ip"), client.get("port")) as s:

        send_message(s, message)
        request_confirmed = read_confirmation_message(s)

        if(request_confirmed):
            start_wave_receiver()
        else:
            print("Client no longer available")
            return

        s.settimeout(0.1)
        done_message = False
        while True:

            with contextlib.suppress(socket.timeout):
                i, o, e = select.select( [sys.stdin], [], [], 1 )

                if (i):
                    if(sys.stdin.readline().strip() == ("q")):
                        break

                if(done_message == False):
                    done_message = read_done_message(s)

                if(done_message and frames.empty()):
                    break

        finish["receive"] = True
        

    logger.info("request_song message sent")
    
def read_done_message(s):
    request_bytes = s.recv(4096)
    if not request_bytes:
        return

    request = json.loads(request_bytes)

    match request.get("message"):
        case "DONE":
            return True
        case message:
            logger.info("Expected 'DONE, received" + message)
            return False
    
def get_song_input():
    
    print_known_clients()
    
    client_index = int(input("Input a client number: "))

    print(f"Client {client_index} musics: ")
    for i in range(len(list(known_clients[client_index].get('songs')))):
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

    
def print_known_clients():
    for i in range(len(known_clients)):
        print(f"Client {i}: ", end="")
        print(known_clients[i])
        print()

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
    global my_p2p_port
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
