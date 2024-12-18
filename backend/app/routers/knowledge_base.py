from fastapi import Depends, HTTPException, APIRouter
from typing import Annotated, List

from app.dependencies import Authorize, EmbeddingModelDep, ServerConfigDep

from ..knowledge_base.knowledge_base_model import (
    KnowledgeBaseItem,
    KnowledgeBaseItemHeader,
)
from ..knowledge_base.knowledge_base_service import KnowledgeBaseService


class NotFoundError(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Item not found")


ITEM_ID_PATH = "/{item_id}"
router = APIRouter(
    tags=["Knowledge Base"],
    dependencies=[Depends(Authorize("admin"))],
)


def get_knowledge_base_service(
    embedding_model: EmbeddingModelDep, server_config: ServerConfigDep
):
    return KnowledgeBaseService(embedding_model, server_config.knowledge_base)


KnowledgeBaseServiceDep = Annotated[
    KnowledgeBaseService, Depends(get_knowledge_base_service)
]


@router.post("", response_model=KnowledgeBaseItem)
def create_item(service: KnowledgeBaseServiceDep, item: KnowledgeBaseItem):
    """
    Create a new knowledge base item.
    """
    return service.create_item(item)


@router.get("")
def get_items(service: KnowledgeBaseServiceDep) -> List[KnowledgeBaseItemHeader]:
    """
    Get all knowledge base items.
    """
    return service.get_items()


@router.get(ITEM_ID_PATH, response_model=KnowledgeBaseItem)
def get_item(service: KnowledgeBaseServiceDep, item_id: str):
    """
    Get a knowledge base item by ID.
    """
    item = service.get_item(item_id)
    if not item:
        raise NotFoundError
    return item


@router.put(ITEM_ID_PATH, response_model=KnowledgeBaseItem)
def update_item(
    service: KnowledgeBaseServiceDep, item_id: str, updated_item: KnowledgeBaseItem
):
    """
    Update a knowledge base item.
    """
    updated_item = service.update_item(item_id, updated_item)
    if not updated_item:
        raise NotFoundError
    return updated_item


@router.delete(ITEM_ID_PATH, response_model=bool)
def delete_item(service: KnowledgeBaseServiceDep, item_id: str):
    """
    Delete a knowledge base item.
    """
    success = service.delete_item(item_id)
    if not success:
        raise NotFoundError
    return True
