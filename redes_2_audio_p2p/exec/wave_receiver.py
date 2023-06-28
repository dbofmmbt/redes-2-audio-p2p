import pyaudio
import socket
from threading import Thread
import queue

from .constants import CHANNELS, CHUNK, RECEIVER_PORT, RATE, SAMPLE_WIDTH

frames = queue.Queue()


def receiver(receive_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    with sock:
        sock.bind(("0.0.0.0", receive_port))
        while True:
            payload = sock.recv(CHUNK * CHANNELS * SAMPLE_WIDTH)
            frames.put(payload)


def player(stream: pyaudio.Stream):
    while True:
        stream.write(frames.get(block=True))


def run_audio_receiver(receive_port):
    p = pyaudio.PyAudio()

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
        