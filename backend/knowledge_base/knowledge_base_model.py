from pydantic import BaseModel, ConfigDict, Field
from typing import List, Dict, Optional


class KnowledgeBaseItemHeader(BaseModel):
    """Represents the header of a knowledge base item."""

    item_id: Optional[str] = Field(
        None, description="Unique identifier for the knowledge base item."
    )
    title: str = Field(..., description="Title of the knowledge base item.")
    keywords: Optional[List[str]] = Field(
        default_factory=list, description="List of keywords associated with the item."
    )


class KnowledgeBaseItem(KnowledgeBaseItemHeader):
    """Represents a single item in a knowledge base."""

    content: str = Field(..., description="Content of the knowledge base item.")
    metadata: Optional[Dict[str, str]] = Field(
        default_factory=dict, description="Additional metadata for the item."
    )
