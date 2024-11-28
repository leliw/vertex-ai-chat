import json
import logging
from fastapi import FastAPI, Response
from fastapi.testclient import TestClient
import pytest

from ampf.gcp.ampf_gcp_factory import AmpfGcpFactory
from app.dependencies import get_server_config, get_user_email
from app.routers import chats, chats_message, files


@pytest.fixture
def blob_storage(test_config):
    factory = AmpfGcpFactory()
    blob_storage = factory.create_blob_storage(test_config.file_storage_bucket)
    yield blob_storage
    # Clean up
    blob_storage.drop()


@pytest.fixture
def client(test_config, blob_storage):
    logging.getLogger("ampf").setLevel(logging.DEBUG)
    app = FastAPI()
    app.dependency_overrides[get_server_config] = lambda: test_config
    app.dependency_overrides[get_user_email] = lambda: "test@test.com"
    app.include_router(prefix="/api/chats", router=chats.router)
    app.include_router(
        prefix="/api/chats/{chat_id}/messages", router=chats_message.router
    )
    app.include_router(prefix="/api/files", router=files.router)
    client = TestClient(app)
    yield client
    # Clean up
    blob_storage.delete_folder("test@test.com")


def test_get_new_chat_session(client):
    # When: A GET request is made to /api/chats
    response = client.get("/api/chats/_NEW_")
    # Then: The response status code is 200
    assert 200 == response.status_code
    r = response.json()
    # And: The response contains a chat session
    assert "chat_session_id" in r


@pytest.fixture
def chat_session_id(client):
    """Create a new chat session and return its ID"""
    response = client.get("/api/chats/_NEW_")
    chat_session_id = response.json()["chat_session_id"]
    yield chat_session_id
    # Clean up
    client.delete(f"/api/chats/{chat_session_id}")


def get_answer(response: Response):
    """Extract the answer from the streaming response"""
    r = json.loads(f"[{response.text}]")
    answer = ""
    for i in r:
        answer += i["value"]
    return answer


def test_send_message(client, chat_session_id):
    # When: Message is sent to chat session
    response = client.post(
        f"/api/chats/{chat_session_id}/messages",
        json={
            "author": "user",
            "content": "Kto wynalazł telefon? Podaj samo imię i nazwisko.",
        },
    )
    # Then: The response status code is 200
    assert 200 == response.status_code
    # And: The response contains right answer
    assert "Graham Bell" in get_answer(response)


def test_send_message_with_file(client, chat_session_id):
    # Given: A file
    files = [
        ("files", ("test4.txt", b"File content 4", "text/plain")),
    ]
    # And: The file is uploaded
    client.post("/api/files", files=files)
    # When: Message with file is sent to chat session
    response = client.post(
        f"/api/chats/{chat_session_id}/messages",
        json={
            "author": "user",
            "content": "Jaka jest treść załączonego pliku?",
        },
    )
    # Then: The response status code is 200
    assert 200 == response.status_code
    # And: The response contains right answer
    assert "File content 4" in get_answer(response)
