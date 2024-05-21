from pydantic import BaseModel, Field
from typing import List, Dict


class KnowledgeBaseItem(BaseModel):
    """
    Represents a single item in a knowledge base.
    """

    id: int = Field(..., description="Unique identifier for the knowledge base item.")
    title: str = Field(..., description="Title of the knowledge base item.")
    content: str = Field(..., description="Content of the knowledge base item.")
    keywords: List[str] = Field(
        default_factory=list, description="List of keywords associated with the item."
    )
    metadata: Dict[str, str] = Field(
        default_factory=dict, description="Additional metadata for the item."
    )
