from typing import List, Optional
from uuid import uuid4

from gcp.gcp_storage import Storage


from .knowledge_base_model import KnowledgeBaseItem, KnowledgeBaseItemHeader


class KnowledgeBaseService:
    """
    Service for managing knowledge base items.
    """

    def __init__(self):
        self.storage = Storage("KnowledgeBase", KnowledgeBaseItem, key_name="item_id")

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
        return [KnowledgeBaseItemHeader(**i.model_dump()) for i in self.storage.get_all()]

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
