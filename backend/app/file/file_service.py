import logging
from typing import Iterator
from fastapi import UploadFile
from ampf.base import BaseFactory
from app.config import ServerConfig


class FileService:
    """A service for managing user session files."""

    def __init__(self, config: ServerConfig, factory: BaseFactory, user_email: str):
        self.config = config
        self.factory = factory
        self.user_email = user_email
        self.storage = factory.create_blob_storage(f"users/{self.user_email}/session_files")
        self._log = logging.getLogger(__name__)

    def upload_file(self, file: UploadFile):
        """Upload a file to the user's session storage."""
        self._log.debug("Uploading file %s", file.filename)
        self.storage.upload_blob(file.filename, file.file.read(), content_type=file.content_type)

    def delete_file(self, file_name: str):
        """Delete a file from the user's session storage."""
        self._log.debug("Deleting file %s", file_name)
        self.storage.delete(file_name)

    def get_all_files(self) -> Iterator:
        """Get all files from the user's session storage."""
        self._log.debug("Getting all files for user %s", self.user_email)
        ret = self.storage.list_blobs()
        for f in ret:
            self._log.debug("Found file %s", f)
            yield f
