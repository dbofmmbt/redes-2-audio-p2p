from contextlib import suppress
import logging
import pyaudio
import socket
from threading import Thread
import queue

from .constants import CHANNELS, CHUNK, RECEIVER_PORT, RATE, SAMPLE_WIDTH
from .globals import finish

frames = queue.Queue()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("receiver")

def receiver(receive_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.settimeout(0.01)
    with sock:
        sock.bind(("0.0.0.0", receive_port))
        while not finish["receive"]:
            with suppress(socket.timeout):
                payload, addr = sock.recvfrom(CHUNK * CHANNELS * SAMPLE_WIDTH)
                frames.put(payload)
    
    frames.queue.clear()


def player(stream: pyaudio.Stream):
    while not finish["receive"] :
        with suppress(queue.Empty):
            stream.write(frames.get(block=True, timeout=0.01))


def run_audio_receiver(receive_port):
    p = pyaudio.PyAudio()

    finish["receive"] = False

    stream = p.open(
        format=p.get_format_from_width(SAMPLE_WIDTH),
        channels=CHANNELS,
        rate=RATE,
        output=True,
        frames_per_buffer=CHUNK,
    )

    receiver_thread = Thread(target=receiver, args=(receive_port,))
    player_thread = Thread(target=player, args=(stream,))

    receiver_thread.start()
    player_thread.start()

    receiver_thread.join()
    player_thread.join()


    stream.close()

    p.terminate()
        