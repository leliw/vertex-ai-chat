from typing import Type
from google.cloud import firestore
from pydantic import BaseModel

from ampf.base import AmpfBaseFactory, BaseStorage, BaseBlobStorage
from ampf.gcp import GcpStorage, GcpBlobStorage


# @singleton
class AmpfGcpFactory(AmpfBaseFactory):
    _db = None

    @classmethod
    def init_client(cls):
        if not AmpfGcpFactory._db:
            AmpfGcpFactory._db = firestore.Client()

    def create_storage[T: BaseModel](
        self, collection_name: str, clazz: Type[T], key_name: str = None
    ) -> BaseStorage[T]:
        return GcpStorage(collection_name, clazz, db=AmpfGcpFactory._db, key_name=key_name)

    def create_blob_storage[T: BaseModel](
        self, bucket_name: str, clazz: Type[T] = None, content_type: str = None
    ) -> BaseBlobStorage[T]:
        return GcpBlobStorage(bucket_name, clazz, content_type)
