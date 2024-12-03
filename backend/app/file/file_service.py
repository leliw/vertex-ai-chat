import logging
from typing import Any, Iterator
from fastapi import UploadFile
from ampf.base.ampf_base_factory import AmpfBaseFactory
from app.config import ServerConfig


class FileService:
    """A service for managing user session files."""

    def __init__(self, config: ServerConfig, factory: AmpfBaseFactory, user_email: str):
        self.config = config
        self.factory = factory
        self.storage = factory.create_blob_storage(config.file_storage_bucket)
        self.user_email = user_email
        self._log = logging.getLogger(__name__)

    def upload_file(self, file: UploadFile):
        """Upload a file to the user's session storage."""
        key = f"{self.user_email}/{file.filename}"
        self._log.debug("Uploading file %s", key)
        self.storage.upload_blob(key, file.file.read(), content_type=file.content_type)

    def delete_file(self, file_name: str):
        """Delete a file from the user's session storage."""
        key = f"{self.user_email}/{file_name}"
        self._log.debug("Deleting file %s", key)
        self.storage.delete(key)

    def get_all_files(self) -> Iterator[Any]:
        """Get all files from the user's session storage."""
        self._log.debug("Getting all files for user %s", self.user_email)
        ret = self.storage.list_blobs(f"{self.user_email}/")
        for f in ret:
            self._log.debug("Found file %s", f)
            yield f
