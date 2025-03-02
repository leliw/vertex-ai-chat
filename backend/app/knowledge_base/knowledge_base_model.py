from uuid import uuid4
from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Optional


class KnowledgeBaseItemHeader(BaseModel):
    """Represents the header of a knowledge base item."""

    item_id: Optional[str] = Field(
        description="Unique identifier for the knowledge base item.",
        default_factory=lambda: str(uuid4()),
    )
    title: str = Field(..., description="Title of the knowledge base item.")
    keywords: Optional[List[str]] = Field(
        default_factory=list, description="List of keywords associated with the item."
    )

    @field_validator("item_id", mode="before")
    @classmethod
    def ensure_item_id(cls, value):
        if not value:
            return str(uuid4())
        return value


class KnowledgeBaseItem(KnowledgeBaseItemHeader):
    """Represents a single item in a knowledge base."""

    content: str = Field(..., description="Content of the knowledge base item.")
    metadata: Optional[Dict[str, str]] = Field(
        default_factory=dict, description="Additional metadata for the item."
    )
