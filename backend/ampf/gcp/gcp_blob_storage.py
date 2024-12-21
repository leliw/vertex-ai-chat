import logging
from typing import Any, Iterator, Type
from fastapi import UploadFile

from google.cloud import storage

from ampf.base import BaseBlobStorage, KeyNotExists


class GcpBlobStorage[T](BaseBlobStorage[T]):
    """A simple wrapper around Google Cloud Storage."""

    _storage_client = None

    @classmethod
    def init_client(cls):
        if not GcpBlobStorage._storage_client:
            GcpBlobStorage._storage_client = storage.Client()

    def __init__(
        self, bucket_name: str, clazz: Type[T] = None, content_type: str = None
    ):
        super().__init__(bucket_name, clazz, content_type)
        self._log = logging.getLogger(__name__)
        GcpBlobStorage.init_client()
        self._bucket = GcpBlobStorage._storage_client.bucket(bucket_name)
        if not self._bucket.exists():
            self._bucket.create()
            self._log.warning("Bucket %s created", bucket_name)

    def upload_blob(
        self, key: str, data: bytes, metadata: T = None, content_type: str = None
    ) -> None:
        blob = self._bucket.blob(key)
        if metadata:
            blob.metadata = metadata.dict()
        blob.upload_from_string(data, content_type=content_type or self.contet_type)

    def download_blob(self, key: str) -> bytes:
        blob = self._bucket.blob(key)
        if not blob.exists():
            raise KeyNotExists(self.bucket_name, self.clazz, key)
        return blob.download_as_bytes()

    def put_metadata(self, key: str, metadata: T) -> None:
        blob = self._bucket.blob(key)
        blob.metadata = metadata.dict()
        blob.patch()

    def get_metadata(self, key: str) -> T:
        blob = self._bucket.blob(key)
        if not blob.exists():
            raise KeyNotExists(self.bucket_name, self.clazz, key)
        if not blob.metadata:
            # I don't know why, but sometimes the metadata is None (ML)
            blob.reload()
        if not blob.metadata:
            return None
        return self.clazz(**blob.metadata)

    def delete(self, key: str):
        blob = self._bucket.blob(key)
        blob.delete()

    def keys(self) -> Iterator[str]:
        for blob in self._bucket.list_blobs():
            yield blob.name

    def list_blobs(self, dir: str = None) -> Iterator[Any]:
        prefix = dir if dir[-1] == "/" else dir + "/"
        i = len(prefix)
        for blob in self._bucket.list_blobs(prefix=prefix):
            b: storage.Blob = blob
            yield {"name": b.name[i:], "mime_type": b.content_type, "path": b.name}

    # Additional not tested methods

    def upload(self, file_path: str, file_name: str):
        blob = self._bucket.blob(file_name)
        blob.upload_from_filename(file_path)

    def download(self, file_name: str, dest_path: str):
        blob = self._bucket.blob(file_name)
        blob.download_to_filename(dest_path)

    def get_blob(self, file_name: str):
        return self._bucket.blob(file_name)

    def get_blob_url(self, file_name: str):
        blob = self._bucket.blob(file_name)
        return blob.public_url

    def get_blob_signed_url(self, file_name: str, expiration: int):
        blob = self._bucket.blob(file_name)
        return blob.generate_signed_url(expiration=expiration, method="GET")

    def get_blob_metadata(self, file_name: str):
        blob = self._bucket.blob(file_name)
        return blob.metadata

    def set_blob_metadata(self, file_name: str, metadata: dict):
        blob = self._bucket.blob(file_name)
        blob.metadata = metadata
        blob.patch()

    def copy_blob(self, source_key: str, dest_key: str):
        source_blob = self._bucket.blob(source_key)
        new_blob = self._bucket.copy_blob(source_blob, self._bucket, dest_key)
        return new_blob

    def move_blob(self, source_key: str, dest_key: str):
        source_blob = self._bucket.blob(source_key)
        new_blob = self._bucket.rename_blob(source_blob, dest_key)
        return new_blob

    def upload_blob_from_file(self, file_name: str, upload_file: UploadFile):
        """Upload a file from an UploadFile object."""
        blob = self._bucket.blob(file_name)
        blob.upload_from_file(upload_file.file, content_type=upload_file.content_type)

    def delete_folder(self, folder_name: str):
        blobs = self._bucket.list_blobs(prefix=folder_name)
        for blob in blobs:
            blob.delete()
