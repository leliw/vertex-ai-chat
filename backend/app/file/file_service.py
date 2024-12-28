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
        self.storage = factory.create_blob_storage(config.file_storage_bucket)
        self.user_email = user_email
        self.work_dir = f"users/{self.user_email}/session_files"
        self._log = logging.getLogger(__name__)

    def upload_file(self, file: UploadFile):
        """Upload a file to the user's session storage."""
        key = f"{self.work_dir}/{file.filename}"
        self._log.debug("Uploading file %s", key)
        self.storage.upload_blob(key, file.file.read(), content_type=file.content_type)

    def delete_file(self, file_name: str):
        """Delete a file from the user's session storage."""
        key = f"{self.work_dir}/{file_name}"
        self._log.debug("Deleting file %s", key)
        self.storage.delete(key)

    def get_all_files(self) -> Iterator:
        """Get all files from the user's session storage."""
        self._log.debug("Getting all files for user %s", self.user_email)
        ret = self.storage.list_blobs(self.work_dir)
        for f in ret:
            self._log.debug("Found file %s", f)
            yield f
