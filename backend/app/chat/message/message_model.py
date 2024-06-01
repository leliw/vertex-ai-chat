from typing import Literal, Optional
from pydantic import BaseModel, Field


class ChatMessageFile(BaseModel):
    name: Optional[str] = Field("")
    url: str
    mime_type: str


class ChatMessage(BaseModel):
    author: Literal["user", "ai"]
    content: str
    files: Optional[list[ChatMessageFile]] = Field([])
