"""In memory storage implemenation - for tests"""

from typing import Iterator, Type
from pydantic import BaseModel

from .base import AmpfBaseFactory, BaseStorage, BaseBlobStorage


class InMemoryStorage[T: BaseModel](BaseStorage):
    """In memory storage implementation"""

    def __init__(self, clazz: Type[T], key_name: str = None):
        super().__init__(clazz, key_name)
        self.items = {}

    def put(self, key: str, value: T) -> None:
        self.items[key] = value.model_copy(deep=True)

    def get(self, key: str) -> T:
        ret = self.items.get(key)
        if ret:
            return ret.model_copy(deep=True)
        else:
            return None

    def keys(self) -> Iterator[T]:
        return self.items.keys()

    def delete(self, key: str) -> None:
        self.items.pop(key, None)

    def is_empty(self) -> bool:
        return not bool(self.items)

    def drop(self):
        self.items = {}


class InMemoryBlobStorage[T: BaseModel](BaseBlobStorage):
    """In memory blob storage implementation"""

    buckets = {}

    def __init__(self, bucket_name: str, clazz: Type[T], content_type: str = None):
        self.bucket_name = bucket_name
        self.clazz = clazz
        self.contet_type = content_type

    def upload_blob(
        self, key: str, data: bytes, metadata: T = None, content_type: str = None
    ) -> None:
        if self.bucket_name not in self.buckets:
            self.buckets[self.bucket_name] = {}
        if key not in self.buckets[self.bucket_name]:
            self.buckets[self.bucket_name][key] = {}
        self.buckets[self.bucket_name][key]["data"] = data
        if metadata:
            self.buckets[self.bucket_name][key]["metadata"] = metadata.model_copy(
                deep=True
            )
        if content_type:
            self.buckets[self.bucket_name][key]["content_type"] = content_type

    def download_blob(self, key: str) -> bytes:
        return self.buckets[self.bucket_name][key]["data"]

    def put_metadata(self, key: str, metadata: T) -> None:
        self.buckets[self.bucket_name][key]["metadata"] = metadata.model_copy(deep=True)

    def get_metadata(self, key: str) -> T:
        return self.buckets[self.bucket_name][key]["metadata"]

    def delete(self, key: str):
        self.buckets[self.bucket_name].pop(key, None)

    def keys(self) -> Iterator[str]:
        return self.buckets[self.bucket_name].keys()

    def drop(self) -> None:
        self.buckets.pop(self.bucket_name, None)

    def list_blobs(self, dir: str = None) -> Iterator[str]:
        if self.bucket_name not in self.buckets:
            return
        for k in self.buckets[self.bucket_name].keys():
            prefix = dir if dir[-1] == "/" else dir + "/"
            i = len(prefix) if prefix else 0
            if not prefix or k.startswith(prefix):
                yield {
                    "name": k[i:],
                    "mime_type": self.buckets[self.bucket_name][k]["content_type"],
                }

    def move_blob(self, source_key: str, dest_key: str):
        self.buckets[self.bucket_name][dest_key] = self.buckets[self.bucket_name].pop(
            source_key
        )


class AmpfInMemoryFactory(AmpfBaseFactory):
    collections = {}

    def create_storage[T: BaseModel](
        self, collection_name: str, clazz: Type[T], key_name: str = None
    ) -> BaseStorage[T]:
        if collection_name not in self.collections:
            self.collections[collection_name] = InMemoryStorage(
                clazz=clazz, key_name=key_name
            )
        return self.collections.get(collection_name)

    def create_blob_storage[T: BaseModel](
        self, bucket_name: str, clazz: Type[T] = None, content_type: str = None
    ) -> BaseBlobStorage[T]:
        return InMemoryBlobStorage(bucket_name, clazz, content_type)
