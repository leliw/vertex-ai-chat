from io import BytesIO
from fastapi import UploadFile
import pytest

from app.config import ServerConfig
from app.file.file_service import FileService


@pytest.fixture
def file_service(test_config: ServerConfig, factory, user_email) -> FileService:
    return FileService(test_config, factory, user_email)


def test_happy_path(file_service):
    # Given: Uploaded file
    file = UploadFile(
        filename="test1.txt",
        file=BytesIO(b"File content 1"),
        headers={"content-type": "text/plain"},
    )
    file_service.upload_file(file)
    # When: Get all files
    files = list(file_service.get_all_files())
    # Then: One file is returned
    assert len(list(files)) == 1
    file_service.delete_file("test1.txt")
