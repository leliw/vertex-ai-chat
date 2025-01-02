from typing import List
from ampf.gcp import GcpStorage
from haintech.ai.base.base_ai_text_embedding_model import BaseAITextEmbeddingModel
from .knowledge_base_model import KnowledgeBaseItem
from google.cloud.firestore_v1.vector import Vector
from google.cloud.firestore_v1.vector_query import VectorQuery
from google.cloud.firestore_v1.base_vector_query import DistanceMeasure


class KnowledgeBaseStorage(GcpStorage):
    """Storage for knowledge base items."""

    def __init__(
        self,
        embedding_model: BaseAITextEmbeddingModel,
        embedding_search_limit: int = 5,
    ):
        super().__init__("KnowledgeBase", KnowledgeBaseItem, key_name="item_id")
        self.embedding_search_limit = embedding_search_limit
        self.embedding_model = embedding_model

    async def on_before_save(self, item: dict) -> dict:
        """Calculate embedding vector before saving data to Firestore."""
        item["embedding"] = Vector(
            await self.embedding_model.get_embedding(text=item["content"])
        )
        return item

    async def find_nearest(
        self, text: str, keywords: List[str] = None, limit: int = None
    ) -> List[KnowledgeBaseItem]:
        """Finds the nearest knowledge base items to the given string.

        Args:
            text: The text to search for.
            keywords: A list of keywords (any of) to filter the search results."""
        embedding = await self.embedding_model.get_embedding(text=text)
        vq: VectorQuery = self._coll_ref.find_nearest(
            vector_field="embedding",
            query_vector=Vector(embedding),
            distance_measure=DistanceMeasure.COSINE,
            limit=limit or self.embedding_search_limit,
        ).get()
        if keywords:
            ret = []
            for ds in vq:
                kb = KnowledgeBaseItem(**ds.to_dict())
                if any(keyword in kb.keywords for keyword in keywords):
                    ret.append(kb)
        else:
            ret = [KnowledgeBaseItem(**ds.to_dict()) for ds in vq]
        return ret

    # Async methods of superclass
    async def save(self, value: KnowledgeBaseItem) -> None:
        key = self.get_key(value)
        await self.put(key, value)

    async def put(self, key: str, data: KnowledgeBaseItem) -> None:
        """Put a document in the collection."""
        data_dict = data.model_dump(by_alias=True, exclude_none=True)
        data_dict = await self.on_before_save(data_dict)  # Preprocess data
        self._coll_ref.document(key).set(data_dict)
