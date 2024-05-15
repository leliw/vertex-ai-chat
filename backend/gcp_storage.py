"""A simple wrapper around Google Cloud Firestore."""

from typing import Generic, Iterator, Type
from google.cloud import firestore

from storage import T, BaseStorage


class Storage(BaseStorage[T], Generic[T]):
    """A simple wrapper around Google Cloud Firestore."""

    def __init__(
        self,
        collection: str,
        clazz: Type[T],
        project: str = None,
        database: str = None,
        key_name: str = None,
    ):
        super().__init__(clazz, key_name=key_name)
        self._db = firestore.Client(project=project, database=database)
        self._collection = collection
        self._coll_ref = self._db.collection(self._collection)

    def put(self, key: str, data: T) -> None:
        """Put a document in the collection."""
        self._coll_ref.document(key).set(
            data.model_dump(by_alias=True, exclude_none=True)
        )

    def get(self, key: str) -> T:
        """Get a document from the collection."""
        data = self._coll_ref.document(key).get().to_dict()
        if not data:
            return
        return self.clazz.model_validate(data)

    def get_all(self, order_by: list[str | tuple[str, any]] = None) -> Iterator[T]:
        """Get all documents from the collection."""
        coll_ref = self._coll_ref
        if order_by:
            for o in order_by:
                if isinstance(o, tuple):
                    coll_ref = coll_ref.order_by(o[0], direction=o[1])
                else:
                    coll_ref = coll_ref.order_by(o)
        for doc in coll_ref.stream():
            yield self.clazz.model_validate(doc.to_dict())

    def keys(self) -> Iterator[str]:
        """Return a list of keys in the collection."""
        for doc in self._coll_ref.stream():
            yield doc.id

    def delete(self, key: str) -> None:
        """Delete a document from the collection."""
        self._coll_ref.document(key).delete()

    def drop(self) -> None:
        """Delete all documents from the collection."""
        for doc in self._coll_ref.stream():
            doc.reference.delete()
