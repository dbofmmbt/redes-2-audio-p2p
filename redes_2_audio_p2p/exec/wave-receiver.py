import pyaudio
import socket
from threading import Thread
import queue

from .constants import CHANNELS, CHUNK, RECEIVER_PORT, RATE, SAMPLE_WIDTH

frames = queue.Queue()


def receiver():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    with sock:
        sock.bind(("0.0.0.0", RECEIVER_PORT))
        while True:
            payload = sock.recv(CHUNK * CHANNELS * SAMPLE_WIDTH)
            frames.put(payload)


def player(stream: pyaudio.Stream):
    while True:
        stream.write(frames.get(block=True))


p = pyaudio.PyAudio()

stream = p.open(
    format=p.get_format_from_width(SAMPLE_WIDTH),
    channels=CHANNELS,
    rate=RATE,
    output=True,
    frames_per_buffer=CHUNK,
)

receiver_thread = Thread(target=receiver)
player_thread = Thread(target=player, args=(stream,))

receiver_thread.start()
player_thread.start()

receiver_thread.join()
player_thread.join()

stream.close()

p.terminate()
