import logging
from typing import Iterator, Type
from fastapi import UploadFile

from google.cloud import storage

from ampf.base import BaseBlobStorage, KeyNotExists


class GcpBlobStorage[T](BaseBlobStorage[T]):
    """A simple wrapper around Google Cloud Storage."""

    def __init__(self, bucket_name: str, clazz: Type[T], content_type: str = None):
        super().__init__(bucket_name, clazz, content_type)
        self._log = logging.getLogger(__name__)
        self._storage_client = storage.Client()
        self._bucket = self._storage_client.bucket(bucket_name)

        if not self._bucket.exists():
            self._bucket.create()
            self._log.warning("Bucket %s created", bucket_name)

    def upload_blob(self, key: str, data: bytes, metadata: T = None) -> None:
        blob = self._bucket.blob(key)
        if metadata:
            blob.metadata = metadata.dict()
        blob.upload_from_string(data, content_type=self.contet_type)

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
