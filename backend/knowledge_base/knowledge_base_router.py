from fastapi import HTTPException, APIRouter
from typing import List

from .knowledge_base import KnowledgeBaseItem
from .knowledge_base_service import KnowledgeBaseService


class NotFoundError(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Item not found")


class KnowledgeBaseRouter:
    """
    Class-based router for knowledge base endpoints.
    """

    def __init__(self):
        """
        Initializes the router with a KnowledgeBaseService instance.
        """
        ITEM_ID_PATH = "/{item_id}"

        self.service = KnowledgeBaseService()

        self.router = APIRouter(
            prefix="/knowledge-base",
            tags=["Knowledge Base"],
        )
        self.router.post("/", response_model=KnowledgeBaseItem)(self.create_item)
        self.router.get(ITEM_ID_PATH, response_model=KnowledgeBaseItem)(self.get_item)
        self.router.get("/", response_model=List[KnowledgeBaseItem])(self.get_items)
        self.router.put(ITEM_ID_PATH, response_model=KnowledgeBaseItem)(
            self.update_item
        )
        self.router.delete(ITEM_ID_PATH, response_model=bool)(self.delete_item)

    def create_item(self, item: KnowledgeBaseItem):
        """
        Create a new knowledge base item.
        """
        return self.service.create_item(item)

    def get_item(self, item_id: int):
        """
        Get a knowledge base item by ID.
        """
        item = self.service.get_item(item_id)
        if not item:
            raise NotFoundError
        return item

    def get_items(self):
        """
        Get all knowledge base items.
        """
        return self.service.get_items()

    def update_item(self, item_id: int, updated_item: KnowledgeBaseItem):
        """
        Update a knowledge base item.
        """
        updated_item = self.service.update_item(item_id, updated_item)
        if not updated_item:
            raise NotFoundError
        return updated_item

    def delete_item(self, item_id: int):
        """
        Delete a knowledge base item.
        """
        success = self.service.delete_item(item_id)
        if not success:
            raise NotFoundError
        return True
