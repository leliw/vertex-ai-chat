from typing import List
from ampf.gcp import GcpStorage
from .knowledge_base_model import KnowledgeBaseItem
from haintech.ai import AiFactory
from google.cloud.firestore_v1.vector import Vector
from google.cloud.firestore_v1.vector_query import VectorQuery
from google.cloud.firestore_v1.base_vector_query import DistanceMeasure


class KnowledgeBaseStorage(GcpStorage):
    """Storage for knowledge base items."""

    def __init__(
        self,
        ai_factory: AiFactory = None,
        embedding_model: str = "text-multilingual-embedding-002",
        embedding_search_limit: int = 5,
    ):
        super().__init__("KnowledgeBase", KnowledgeBaseItem, key_name="item_id")
        self.ai_factory = ai_factory
        self.embedding_model = embedding_model
        self.embedding_search_limit = embedding_search_limit

    def on_before_save(self, item: dict) -> dict:
        """Calculate embedding vector before saving data to Firestore."""
        item["embedding"] = Vector(
            self.ai_factory.embed_text(
                title=item["title"],
                text=item["content"],
                model_name=self.embedding_model,
            )
        )
        return item

    def find_nearest(
        self, text: str, keywords: List[str] = None
    ) -> List[KnowledgeBaseItem]:
        """Finds the nearest knowledge base items to the given string.

        Args:
            text: The text to search for.
            keywords: A list of keywords (any of) to filter the search results."""
        embedding = self.ai_factory.embed_text(
            text=text, model_name=self.embedding_model, task="QUESTION_ANSWERING"
        )
        vq: VectorQuery = self._coll_ref.find_nearest(
            vector_field="embedding",
            query_vector=Vector(embedding),
            distance_measure=DistanceMeasure.COSINE,
            limit=self.embedding_search_limit,
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
