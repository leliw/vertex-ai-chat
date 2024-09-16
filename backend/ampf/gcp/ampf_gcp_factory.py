from typing import Type
from google.cloud import firestore
from pydantic import BaseModel

from ampf.base import AmpfBaseFactory, BaseStorage
from ampf.gcp import GcpStorage


class AmpfGcpFactory(AmpfBaseFactory):
    def __init__(self, project: str = None, database: str = None):
        self._db = firestore.Client(project=project, database=database)

    def create_storage[T: BaseModel](
        self, collection_name: str, clazz: Type[T], key_name: str = None
    ) -> BaseStorage[T]:
        return GcpStorage(collection_name, clazz, db=self._db, key_name=key_name)