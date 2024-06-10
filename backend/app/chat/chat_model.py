from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from .message import ChatMessage


class ChatSessionHeader(BaseModel):
    chat_session_id: str
    user: str
    created: datetime
    summary: Optional[str] = Field("")


class ChatSession(ChatSessionHeader):
    history: list[ChatMessage]
