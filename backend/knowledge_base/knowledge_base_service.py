from typing import List, Optional


from .knowledge_base import KnowledgeBaseItem


class KnowledgeBaseService:
    """
    Service for managing knowledge base items.
    """

    def __init__(self):
        """
        Initializes the KnowledgeBaseService.
        For simplicity, we'll use an in-memory list to store the items.
        In a real-world application, you'd likely use a database.
        """
        self.items: List[KnowledgeBaseItem] = []
        self.next_id = 1

    def create_item(self, item: KnowledgeBaseItem) -> KnowledgeBaseItem:
        """
        Creates a new knowledge base item.
        """
        item.id = self.next_id
        self.next_id += 1
        self.items.append(item)
        return item

    def get_item(self, item_id: int) -> Optional[KnowledgeBaseItem]:
        """
        Retrieves a knowledge base item by its ID.
        """
        for item in self.items:
            if item.id == item_id:
                return item
        return None

    def get_items(self) -> List[KnowledgeBaseItem]:
        """
        Returns all knowledge base items.
        """
        return self.items

    def update_item(
        self, item_id: int, updated_item: KnowledgeBaseItem
    ) -> Optional[KnowledgeBaseItem]:
        """
        Updates an existing knowledge base item.
        """
        for i, item in enumerate(self.items):
            if item.id == item_id:
                updated_item.id = item_id  # Ensure ID is not changed
                self.items[i] = updated_item
                return updated_item
        return None

    def delete_item(self, item_id: int) -> bool:
        """
        Deletes a knowledge base item.
        """
        for i, item in enumerate(self.items):
            if item.id == item_id:
                del self.items[i]
                return True
        return False
