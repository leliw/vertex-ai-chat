import logging
from typing import List, Optional
from uuid import uuid4

from ai_model import AIModelFactory

from .knowledge_base_storage import KnowledgeBaseStorage
from .knowledge_base_model import KnowledgeBaseItem, KnowledgeBaseItemHeader

from app.config import KnowledgeBaseConfig


class KnowledgeBaseService:
    """
    Service for managing knowledge base items.
    """

    def __init__(self, config: KnowledgeBaseConfig):
        self.vertex_ai_fatory = AIModelFactory()
        self.storage = KnowledgeBaseStorage(
            self.vertex_ai_fatory, **config.model_dump()
        )
        self._log = logging.getLogger(__name__)

    def create_item(self, item: KnowledgeBaseItem) -> KnowledgeBaseItem:
        """
        Creates a new knowledge base item.
        """
        item.item_id = str(uuid4())
        self.storage.save(item)
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

    def update_item(
        self, item_id: str, updated_item: KnowledgeBaseItem
    ) -> Optional[KnowledgeBaseItem]:
        """
        Updates an existing knowledge base item.
        """
        if not updated_item.item_id:
            updated_item.item_id = item_id
        self.storage.put(item_id, updated_item)
        return updated_item

    def delete_item(self, item_id: str) -> bool:
        """
        Deletes a knowledge base item.
        """
        return self.storage.delete(item_id)
