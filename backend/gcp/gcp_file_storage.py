from fastapi import UploadFile
from google.cloud import storage

class FileStorage():
    """A simple wrapper around Google Cloud Storage."""
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        self._storage_client = storage.Client()
        self._bucket = self._storage_client.bucket(bucket_name)

    def upload(self, file_path: str, file_name: str):
        blob = self._bucket.blob(file_name)
        blob.upload_from_filename(file_path)
    
    def download(self, file_name: str, dest_path: str):
        blob = self._bucket.blob(file_name)
        blob.download_to_filename(dest_path)
    
    def delete(self, file_name: str):
        blob = self._bucket.blob(file_name)
        blob.delete()

    def list_files(self):
        return [blob.name for blob in self._bucket.list_blobs()]
    
    def get_blob(self, file_name: str):
        return self._bucket.blob(file_name)
    
    def get_blob_url(self, file_name: str):
        blob = self._bucket.blob(file_name)
        return blob.public_url
    
    def get_blob_signed_url(self, file_name: str, expiration: int):
        blob = self._bucket.blob(file_name)
        return blob.generate_signed_url(expiration=expiration, method='GET')
    
    def get_blob_metadata(self, file_name: str):
        blob = self._bucket.blob(file_name)
        return blob.metadata
    
    def set_blob_metadata(self, file_name: str, metadata: dict):
        blob = self._bucket.blob(file_name)
        blob.metadata = metadata
        blob.patch()

    def copy_blob(self, source_file_name: str, dest_file_name: str):
        source_blob = self._bucket.blob(source_file_name)
        new_blob = self._bucket.copy_blob(source_blob, self._bucket, dest_file_name)
        return new_blob
    
    def move_blob(self, source_file_name: str, dest_file_name: str):
        source_blob = self._bucket.blob(source_file_name)
        new_blob = self._bucket.rename_blob(source_blob, dest_file_name)
        return new_blob
    
    def download_blob(self, file_name: str):
        blob = self._bucket.blob(file_name)
        return blob.download_as_string()
    
    def upload_blob(self, file_name: str, data: bytes):
        blob = self._bucket.blob(file_name)
        blob.upload_from_string(data)

    def upload_blob_from_file(self, file_name: str, upload_file: UploadFile):
        """Upload a file from an UploadFile object."""
        blob = self._bucket.blob(file_name)
        blob.upload_from_file(upload_file.file, content_type=upload_file.content_type)

    def delete_folder(self, folder_name: str):
        blobs = self._bucket.list_blobs(prefix=folder_name)
        for blob in blobs:
            blob.delete()