from dotenv import load_dotenv
from pydantic import BaseModel
import pytest

from ampf.base import KeyNotExists
from ampf.gcp import GcpBlobStorage


class TC(BaseModel):
    name: str


@pytest.fixture
def storage():
    load_dotenv()
    return GcpBlobStorage("vertex-ai-chat-dev-unit-tests", TC)

def test_download_key_not_exists(storage):
    with pytest.raises(KeyNotExists):
        storage.download_blob("1")

def test_upload_download_delete(storage):
    storage.upload_blob("1", b"test")
    assert storage.download_blob("1") == b"test"
    storage.delete("1")


def test_upload_download_delete_with_metadata(storage):
    storage.upload_blob("1", b"test", TC(name="test"))
    assert storage.download_blob("1") == b"test"
    assert storage.get_metadata("1") == TC(name="test")
    storage.delete("1")

def test_put_get_metadata(storage):
    # Not exists
    with pytest.raises(KeyNotExists):
        storage.get_metadata("1")
    
    # No metadata
    storage.upload_blob("1", b"test")
    assert storage.download_blob("1") == b"test"
    assert not storage.get_metadata("1")
    
    # With metadata
    storage.put_metadata("1", TC(name="test"))
    assert storage.get_metadata("1") == TC(name="test")

    # Clean up
    storage.delete("1")

def test_keys(storage):
    k = list(storage.keys())
    assert 0 == len(k)

    storage.upload_blob("1", b"test", TC(name="test"))
    
    k = list(storage.keys())
    
    assert 1 == len(k)
    assert "1" == k[0]
    
    storage.delete("1")
