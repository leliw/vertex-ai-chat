import logging
from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from ampf.gcp.ampf_gcp_factory import AmpfGcpFactory
from app.dependencies import get_server_config, get_user_email
from app.routers import files


@pytest.fixture
def blob_storage(test_config):
    factory = AmpfGcpFactory()
    return factory.create_blob_storage(test_config.file_storage_bucket)


@pytest.fixture
def client(test_config, blob_storage):
    logging.getLogger("ampf").setLevel(logging.DEBUG)
    app = FastAPI()
    app.dependency_overrides[get_server_config] = lambda: test_config
    app.dependency_overrides[get_user_email] = lambda: "test@test.com"
    app.include_router(prefix="/api/files", router=files.router)
    client = TestClient(app)
    yield client
    # Clean up
    blob_storage.delete_folder("test@test.com")


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
