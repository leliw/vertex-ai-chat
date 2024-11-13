"""In memory storage implemenation - for tests"""

from typing import Iterator, Type
from pydantic import BaseModel
from .base.ampf_base_factory import AmpfBaseFactory
from .base.base_storage import BaseStorage


class InMemoryStorage[T: BaseModel](BaseStorage):
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
