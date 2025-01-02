import logging
from typing import List, Optional

from haintech.ai.base.base_ai_text_embedding_model import BaseAITextEmbeddingModel

from .knowledge_base_storage import KnowledgeBaseStorage
from .knowledge_base_model import KnowledgeBaseItem, KnowledgeBaseItemHeader

from app.config import KnowledgeBaseConfig


class KnowledgeBaseService:
    """
    Service for managing knowledge base items.
    """

    def __init__(
        self, embedding_model: BaseAITextEmbeddingModel, config: KnowledgeBaseConfig
    ):
        self.storage = KnowledgeBaseStorage(
            embedding_model, config.embedding_search_limit
        )
        self._log = logging.getLogger(__name__)

    async def create_item(self, item: KnowledgeBaseItem) -> KnowledgeBaseItem:
        """
        Creates a new knowledge base item.
        """
        await self.storage.save(item)
        return item

    def get_item(self, item_id: str) -> Optional[KnowledgeBaseItem]:
        """
        Retrieves a knowledge base item by its ID.
        """
        return self.storage.get(item_id)

    def get_items(self) -> List[KnowledgeBaseItemHeader]:
        """
        Returns all knowledge base items.
        """
        return [
            KnowledgeBaseItemHeader(**i.model_dump()) for i in self.storage.get_all()
        ]

    async def update_item(
        self, item_id: str, updated_item: KnowledgeBaseItem
    ) -> Optional[KnowledgeBaseItem]:
        """
        Updates an existing knowledge base item.
        """
        if not updated_item.item_id:
            updated_item.item_id = item_id
        await self.storage.put(item_id, updated_item)
        return updated_item

    def delete_item(self, item_id: str) -> bool:
        """
        Deletes a knowledge base item.
        """
        return self.storage.delete(item_id)

    async def find_nearest(
        self, text: str, keywords: List[str] = None, limit: int = None
    ) -> List[KnowledgeBaseItem]:
        """
        Finds the nearest knowledge base items to the given string.
        """
        return await self.storage.find_nearest(text, keywords, limit)
