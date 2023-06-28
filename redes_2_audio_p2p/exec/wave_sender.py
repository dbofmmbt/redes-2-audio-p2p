"""PyAudio Example: Play a wave file."""

from time import sleep
import wave
import sys

import socket

from .constants import CHUNK, RECEIVER_PORT, SENDER_PORT

def run_audio_sender(filepath, addr, receiver_port):
    
    with wave.open(filepath, "rb") as wf:
        print(
            f"sample width: {wf.getsampwidth()}; frame rate: {wf.getframerate()}; channels: {wf.getnchannels()}"
        )
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("0.0.0.0", SENDER_PORT))
        total = 0
        with sock:
            while len(payload := wf.readframes(CHUNK)):
                total += len(payload)
                sock.sendto(payload, (addr, receiver_port))
                sleep(0.002)
        print(total)
