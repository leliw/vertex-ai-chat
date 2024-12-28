import logging
from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from ampf.gcp import GcpFactory
from app.dependencies import get_server_config, get_user_email
from app.routers import files

_log = logging.getLogger(__name__)


@pytest.fixture
def blob_storage(test_config):
    GcpFactory.init_client(test_config.file_storage_bucket)
    factory = GcpFactory()
    return factory.create_blob_storage("")


@pytest.fixture
def client(test_config, blob_storage, user_email: str):
    logging.getLogger("ampf").setLevel(logging.DEBUG)
    app = FastAPI()
    app.dependency_overrides[get_server_config] = lambda: test_config
    app.dependency_overrides[get_user_email] = lambda: user_email
    app.include_router(prefix="/api/files", router=files.router)
    client = TestClient(app)
    yield client
    # Clean up test user session_files folder
    blob_storage.delete_folder(f"users/{user_email}/session_files")


def test_upload_files(client):
    # Given: Two files
    files = [
        ("files", ("test1.txt", b"File content 1", "text/plain")),
        ("files", ("test2.txt", b"File content 2", "text/plain")),
    ]
    # When: A POST request is made to /api/files
    response = client.post("/api/files", files=files)
    # Then: The response status code is 200
    assert 200 == response.status_code


def test_get_all_files(client):
    # Given: A file
    files = [
        ("files", ("test3.txt", b"File content 3", "text/plain")),
    ]
    # And: The file is uploaded
    client.post("/api/files", files=files)
    # When: List of files is got
    response = client.get("/api/files")
    ret = response.json()
    # Then: The response status code is 200
    assert 200 == response.status_code
    # And: File name is returned
    _log.debug(ret)
    assert "test3.txt" == ret[0]["name"]


def test_delete_file(client):
    # Given: A file
    files = [
        ("files", ("test3.txt", b"File content 3", "text/plain")),
    ]
    # And: The file is uploaded
    client.post("/api/files", files=files)
    # When: A DELETE request is made to /api/files/test3.txt
    response = client.delete("/api/files/test3.txt")
    # Then: The response status code is 200
    assert 200 == response.status_code
