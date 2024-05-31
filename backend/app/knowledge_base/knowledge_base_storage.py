from typing import List
from gcp import Storage
from .knowledge_base_model import KnowledgeBaseItem
from verrtex_ai.vertex_ai_factory import VertexAiFactory
from google.cloud.firestore_v1.vector import Vector
from google.cloud.firestore_v1.vector_query import VectorQuery
from google.cloud.firestore_v1.base_vector_query import DistanceMeasure


class KnowledgeBaseStorage(Storage):
    """Storage for knowledge base items."""

    def __init__(
        self,
        vertex_ai_fatory: VertexAiFactory = None,
        embedding_model: str = "text-multilingual-embedding-002",
        embedding_search_limit: int = 5,
    ):
        super().__init__("KnowledgeBase", KnowledgeBaseItem, key_name="item_id")
        self.vertex_ai_fatory = (
            vertex_ai_fatory if vertex_ai_fatory else VertexAiFactory()
        )
        self.embedding_model = embedding_model
        self.embedding_search_limit = embedding_search_limit

    def on_before_save(self, item: dict) -> dict:
        """Calculate embedding vector before saving data to Firestore."""
        item["embedding"] = Vector(
            self.vertex_ai_fatory.embed_text(
                title=item["title"],
                text=item["content"],
                model_name=self.embedding_model,
            )
        )
        return item

    def find_nearest(self, text: str) -> List[KnowledgeBaseItem]:
        """Finds the nearest knowledge base items to the given string."""
        embedding = self.vertex_ai_fatory.embed_text(
            text=text, model_name=self.embedding_model
        )
        vq: VectorQuery = self._coll_ref.find_nearest(
            vector_field="embedding",
            query_vector=Vector(embedding),
            distance_measure=DistanceMeasure.EUCLIDEAN,
            limit=self.embedding_search_limit,
        ).get()
        ret = [KnowledgeBaseItem(**ds.to_dict()) for ds in vq]
        return ret
