import contextlib
import os
from signal import SIGINT
import socket
import subprocess

import pytest

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# this improves test message a lot
pytest.register_assert_rewrite("tests.util")


@pytest.fixture(autouse=True, scope="session")
def run_server():
    try:
        logger.info("Running server to start testing")
        process = subprocess.Popen(
            ["poetry", "run", "python", "-m", "redes_2_audio_p2p.exec.server"],
            env={**os.environ, "TEST": "true"},
        )

        while True:
            with socket.socket() as s:
                with contextlib.suppress(ConnectionRefusedError):
                    s.connect(("localhost", 8080))
                    logger.info("Startup checks passed")
                    break
        yield
    finally:
        logger.info("stopping process")
        process.send_signal(SIGINT)
        process.wait()
