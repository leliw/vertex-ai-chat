from datetime import datetime
from typing import Optional
from uuid import uuid4
from pydantic import BaseModel, Field

from .message import ChatMessage


class ChatSessionHeader(BaseModel):
    chat_session_id: str = Field(default_factory=lambda: str(uuid4()))
    user: Optional[str] = Field("")
    created: datetime = Field(default_factory=lambda: datetime.now())
    summary: Optional[str] = Field("")


class ChatSession(ChatSessionHeader):
    history: list[ChatMessage] = Field(default_factory=list)
