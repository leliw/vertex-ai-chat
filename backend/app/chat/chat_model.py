from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field


class ChatSessionHeader(BaseModel):
    chat_session_id: str
    user: str
    created: datetime
    summary: Optional[str] = Field("")


class ChatMessageFile(BaseModel):
    name: Optional[str] = Field("")
    url: str
    mime_type: str


class ChatMessage(BaseModel):
    author: Literal["user", "ai"]
    content: str
    files: Optional[list[ChatMessageFile]] = Field([])


class ChatSession(ChatSessionHeader):
    history: list[ChatMessage]
