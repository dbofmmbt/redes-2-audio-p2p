import pytest
from .util import *


def test_hello_world():
    check(payload={"action": "health"}, expected={"message": "OK"})


def test_register():
    check(
        payload={"action": "register", "songs": ["song1"]},
        expected={"message": "user registered succesfully"},
    )


def test_register_again_fails():
    register_message = {"action": "register", "songs": ["my_song"]}
    with client_conn() as s:
        _ = send_request(s, register_message)
        second_register = send_request(s, register_message)

        assert second_register == {"message": "user already exists"}


def test_unregister():
    check(payload={"action": "unregister"}, expected={"message": "OK"})


def test_unregister_removes_peer():
    client1 = client_connect()
    client2 = client_connect()

    response = send_request(client2, {"action": "list"})
    assert response["peers"] == {}

    send_request(client1, {"action": "register", "songs": ["song_from_client1"]})

    response = send_request(client2, {"action": "list"})
    assert len(response["peers"]) > 0

    send_request(client1, {"action": "unregister"})

    response = send_request(client2, {"action": "list"})
    assert response["peers"] == {}


def test_list_empty():
    check(payload={"action": "list"}, expected={"peers": {}})


def test_list():
    conn1 = client_connect()
    conn2 = client_connect()

    _ = send_request(conn1, {"action": "register", "songs": ["song_from_conn1"]})

    response = send_request(conn2, {"action": "list"})

    conn1.close()
    conn2.close()

    received_songs = []
    for songs in response["peers"].values():
        for song in songs:
            received_songs.append(song)

    assert "song_from_conn1" in received_songs
