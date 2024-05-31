from datetime import datetime
from typing import Iterator
from pydantic import BaseModel
from uuid import uuid4

from google.api_core import exceptions
from google.cloud import firestore
from gcp.gcp_file_storage import FileStorage
from app.knowledge_base import KnowledgeBaseStorage
from verrtex_ai.vertex_ai_factory import VertexAiFactory
from vertexai.generative_models import Content, Part, GenerationResponse

from gcp import Storage

from .chat_model import ChatMessage, ChatMessageFile, ChatSessionHeader, ChatSession


class ChatHistoryException(Exception):
    """Is't strange form of returning history."""

    def __init__(self, chat_session: ChatSession, exception: Exception = None):
        self.chat_session = chat_session
        self.exception = exception


class StreamedEvent(BaseModel):
    type: str
    value: str


class ChatSessionUserError(ValueError):
    def __init__(self):
        super().__init__("Chat session does not belong to the user.")


class ChatService:
    """Service for chat."""

    def __init__(self, file_storage: FileStorage):
        self.factory = VertexAiFactory()
        self.storage = Storage("ChatSessions", ChatSession, key_name="chat_session_id")
        self.knowledge_base_storage = KnowledgeBaseStorage(self.factory)
        self.file_storage = file_storage

    def get_answer(
        self, model_name: str, history: list[ChatMessage], message: ChatMessage
    ) -> tuple[ChatMessage, list[ChatMessage]]:
        """Get an answer from the model."""
        in_history = [self._chat_message_to_content(m) for m in history]
        chat = self.factory.get_chat(model_name=model_name, history=in_history)
        response: GenerationResponse = chat.send_message(message.content, stream=False)
        ret = ChatMessage(author="ai", content=response.text)
        out_history = [self._content_to_chat_message(m, {}) for m in chat.history]
        return (ret, out_history)

    def get_answer_async(
        self,
        model_name: str,
        chat_session: ChatSession,
        message: ChatMessage,
        files: list[ChatMessageFile],
    ) -> Iterator[str]:
        """Get an answer from the model."""
        file_names = {}
        if chat_session and chat_session.history:
            in_history = []
            for m in chat_session.history:
                in_history.append(self._chat_message_to_content(m))
                for f in m.files:
                    file_names[f.url] = f.name
        else:
            in_history = []
        try:
            context = self.get_context(message.content)
            chat = self.factory.get_chat(
                model_name=model_name, history=in_history, context=context
            )
            parts = []
            parts.append(Part.from_text(message.content))
            for file in files:
                chat_blob_name = f"chat-{chat_session.chat_session_id}/{str(uuid4())}"
                self.file_storage.move_blob(file.url, chat_blob_name)
                uri = f"gs://{self.file_storage.bucket_name}/{chat_blob_name}"
                parts.append(Part.from_uri(uri, mime_type=file.mime_type))
                file_names[uri] = file.name
            content = Content(role="user", parts=parts)
            responses = chat.send_message(content, stream=True)
            for response in responses:
                if response.text:
                    yield StreamedEvent(type="text", value=response.text)
                # await asyncio.sleep(0.1)
            out_history = [
                self._content_to_chat_message(m, file_names) for m in chat.history
            ]
            chat_session.history = out_history
            if not chat_session.summary:
                chat_session.summary = out_history[0].content
            self.storage.save(chat_session)
        except Exception as e:
            yield StreamedEvent(type=f"error:{type(e).__name__}", value=str(e))
            raise ChatHistoryException(chat_session, e)
        raise ChatHistoryException(chat_session)

    def get_context(self, text: str) -> str:
        """Get the context of the chat session."""
        neartest = self.knowledge_base_storage.find_nearest(text)
        context = ""
        for n in neartest:
            context += "\n\n# " + n.title + "\n" + n.content + "\n\n"
        return context

    def _chat_message_to_content(self, message: ChatMessage) -> Content:
        """Convert ChatMessage to Content."""
        parts = [Part.from_text(message.content)]
        for file in message.files:
            parts.append(
                Part.from_uri(
                    uri=file.url,
                    mime_type=file.mime_type,
                )
            )
        return Content(
            role=message.author if message.author == "user" else "model",
            parts=parts,
        )

    def _content_to_chat_message(
        self, content: Content, file_names: dict[str, str]
    ) -> ChatMessage:
        """Convert Content to ChatMessage."""
        files = []
        for part in content.parts:
            if part.file_data:
                files.append(
                    ChatMessageFile(
                        name=file_names.get(part.file_data.file_uri, ""),
                        url=part.file_data.file_uri,
                        mime_type=part.file_data.mime_type,
                    )
                )
        return ChatMessage(
            author=content.role if content.role == "user" else "ai",
            content=content.parts[0].text,
            files=files,
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
            for s in self.storage.get_all([("created", firestore.Query.DESCENDING)])
            if s.user == user
        ]
        return ret

    async def get_chat(self, chat_session_id: str, user: str) -> ChatSession:
        """Get chat history by id."""
        if chat_session_id == "_NEW_":
            chat_session_id = str(uuid4())
            chat_session = ChatSession(
                chat_session_id=chat_session_id,
                user=user,
                created=datetime.now(),
                summary="",
                history=[],
            )
        else:
            chat_session = self.storage.get(chat_session_id)
            if chat_session.user != user:
                raise ChatSessionUserError()
        return chat_session

    async def update_chat(
        self, chat_session_id: str, chat_session: ChatSession, user: str
    ) -> None:
        old_session = self.storage.get(chat_session_id)
        if old_session.user != user:
            raise ChatSessionUserError()
        return self.storage.save(chat_session)

    async def delete_chat(self, chat_session_id: str, user: str) -> None:
        """Delete chat history by id."""
        chat_session = self.storage.get(chat_session_id)
        if chat_session.user != user:
            raise ChatSessionUserError()
        chat_session = self.storage.get(chat_session_id)
        for message in chat_session.history:
            for file in message.files:
                try:
                    self.file_storage.delete("/".join(file.url.split("/")[3:]))
                except exceptions.NotFound:
                    pass
        return self.storage.delete(chat_session_id)
