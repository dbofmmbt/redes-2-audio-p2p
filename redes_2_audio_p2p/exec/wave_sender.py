"""PyAudio Example: Play a wave file."""

import threading
from time import sleep
import wave
import sys

import socket

from .constants import CHUNK, RECEIVER_PORT, SENDER_PORT
from .globals import finish


def run_audio_sender(filepath, ip, receiver_port):
    threading.Thread(target=handle, args=(filepath, ip, receiver_port)).start()

def handle(filepath, ip, receiver_port):
    with wave.open(filepath, "rb") as wf:

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #sock.bind(("0.0.0.0", SENDER_PORT))
        total = 0
        with sock:
            while len(payload := wf.readframes(CHUNK)) and not finish["send"]:
                total += len(payload)
                sock.sendto(payload, (ip, receiver_port))
                sleep(0.002)

        finish["send"] = True
