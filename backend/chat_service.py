from datetime import datetime
from typing import Iterator, Optional
from pydantic import BaseModel, Field
from uuid import uuid4

from verrtex_ai.vertex_ai_factory import VertexAiFactory
from vertexai.generative_models import Content, Part, GenerationResponse

from gcp_storage import Storage


class ChatSessionHeader(BaseModel):
    chat_session_id: str
    user: str
    created: datetime
    summary: Optional[str] = Field("")


class ChatMessage(BaseModel):
    author: str
    content: str


class ChatSession(ChatSessionHeader):
    history: list[ChatMessage]


class ChatHistoryException(Exception):
    """Is't strange form of returning history."""

    def __init__(self, chat_session_id: str, history: list[ChatMessage]):
        self.chat_session_id = chat_session_id
        self.history = history


class ChatService:
    """Service for chat."""

    def __init__(self):
        self.factory = VertexAiFactory()
        self.storage = Storage("ChatSessions", ChatSession, key_name="chat_session_id")

    def get_answer(
        self, history: list[ChatMessage], message: ChatMessage
    ) -> tuple[ChatMessage, list[ChatMessage]]:
        """Get an answer from the model."""
        in_history = [self._chat_message_to_content(m) for m in history]
        chat = self.factory.get_chat(history=in_history)
        response: GenerationResponse = chat.send_message(message.content, stream=False)
        ret = ChatMessage(author="ai", content=response.text)
        out_history = [self._content_to_chat_message(m) for m in chat.history]
        return (ret, out_history)

    def get_answer_async(
        self,
        history: list[ChatMessage],
        message: ChatMessage,
        chat_session_id: str = None,
        user: str = "Anonymous",
    ) -> Iterator[str]:
        """Get an answer from the model."""
        if chat_session_id:
            chat_session = self.storage.get(chat_session_id)
            history = chat_session.history
        else:
            chat_session_id = str(uuid4())
            chat_session = ChatSession(
                chat_session_id=chat_session_id,
                user=user,
                created=datetime.now(),
                summary=message.content,
                history=[],
            )
        in_history = [self._chat_message_to_content(m) for m in history]
        chat = self.factory.get_chat(history=in_history)
        responses = chat.send_message(message.content, stream=True)
        for response in responses:
            yield response.text
            # await asyncio.sleep(0.1)
        out_history = [self._content_to_chat_message(m) for m in chat.history]
        chat_session.history = out_history
        self.storage.save(chat_session)
        raise ChatHistoryException(chat_session_id, out_history)

    def _chat_message_to_content(self, message: ChatMessage) -> Content:
        """Convert ChatMessage to Content."""
        return Content(
            role=message.author if message.author == "user" else "model",
            parts=[Part.from_text(message.content)],
        )

    def _content_to_chat_message(self, content: Content) -> ChatMessage:
        """Convert Content to ChatMessage."""
        return ChatMessage(
            author=content.role if content.role == "user" else "ai",
            content=content.parts[0].text,
        )

    async def get_all(self, user: str) -> list[ChatSessionHeader]:
        """Get all chat sessions for the user."""
        ret = [
            ChatSessionHeader(
                chat_session_id=s.chat_session_id,
                user=s.user,
                created=s.created,
                summary=s.summary,
            )
            for s in self.storage.get_all()
            if s.user == user
        ]
        return ret

    async def get_chat(self, chat_id: str, user: str) -> list[ChatMessage]:
        """Get chat history by id."""
        chat_session = self.storage.get(chat_id)
        if chat_session.user != user:
            raise ValueError("Chat session does not belong to the user.")
        return chat_session.history

    async def delete_chat(self, chat_id: str, user: str) -> None:
        """Delete chat history by id."""
        chat_session = self.storage.get(chat_id)
        if chat_session.user != user:
            raise ValueError("Chat session does not belong to the user.")
        return self.storage.delete(chat_id)
