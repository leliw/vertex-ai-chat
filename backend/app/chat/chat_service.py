import logging
from typing import AsyncIterator
from pydantic import BaseModel

from google.api_core import exceptions
from google.cloud import firestore
from google.generativeai.types import ContentDict, BlobDict

from ai_agents import AIAgent
from ampf.base import BaseFactory, BaseBlobStorage
from app.agent.agent_model import Agent
from app.knowledge_base import KnowledgeBaseStorage
from haintech.ai import AiFactory

from app.config import ServerConfig
from haintech.ai.base.base_ai_text_embedding_model import BaseAITextEmbeddingModel
from .chat_model import ChatSessionHeader, ChatSession
from .message import ChatMessage, ChatMessageFile


class StreamedEvent(BaseModel):
    type: str
    value: str


class ChatSessionUserError(ValueError):
    def __init__(self):
        super().__init__("Chat session does not belong to the user.")


class ChatService:
    """Service for chat."""

    def __init__(
        self,
        factory: BaseFactory,
        ai_factory: AiFactory,
        embedding_model: BaseAITextEmbeddingModel,
        file_storage: BaseBlobStorage,
        config: ServerConfig,
        user_email: str,
    ):
        self.ai_factory = ai_factory
        self.role = ""
        self.storage = factory.create_storage(
            "ChatSessions", ChatSession, key_name="chat_session_id"
        )
        self.knowledge_base_storage = KnowledgeBaseStorage(
            embedding_model,
            embedding_search_limit=config.knowledge_base.embedding_search_limit,
        )
        self.file_storage = file_storage
        self.user_email = user_email
        self._log = logging.getLogger(__name__)

    def get_answer(
        self, model_name: str, history: list[ChatMessage], message: ChatMessage
    ) -> tuple[ChatMessage, list[ChatMessage]]:
        """Get an answer from the model."""
        ai_agent = AIAgent(model_name=model_name)
        in_history = [m.to_content() for m in history]
        chat = ai_agent.start_chat(history=in_history)
        response = chat.send_message(message.content)
        ret = ChatMessage(author="ai", content=response)
        out_history = [ChatMessage.from_content(m, {}) for m in chat.get_history()]
        return (ret, out_history)

    async def get_answer_async(
        self,
        message: ChatMessage,
        files: list[ChatMessageFile],
        agent: Agent = None,
        model_name: str = None,
        chat_session: ChatSession = None,
    ) -> AsyncIterator[StreamedEvent]:
        """Get an answer from the model."""
        file_names = {}
        in_history = []
        if not chat_session:
            chat_session = ChatSession()
        if chat_session.history:
            for m in chat_session.history:
                in_history.append(m.to_content())
                for f in m.files:
                    file_names[f.url] = f.name
        if agent:
            model_name = agent.model_name
        try:
            context = await self.get_context(message.content, agent)
            ai_agent = AIAgent(model_name=model_name, system_instruction=context)
            chat = ai_agent.start_chat(history=in_history)
            parts = [message.content]
            # Iterate over the user (session) files
            for file in files:
                # Move the file to the chat session directory
                # file_name = f"users/{self.user_email}/session_files/{file.name}"
                chat_blob_name = f"users/{self.user_email}/chats/{chat_session.chat_session_id}/files/{file.name}"
                # file.url = chat_blob_name
                self._log.debug("Moving file %s to %s", file.name, chat_blob_name)
                self.file_storage.move_blob(
                    f"users/{self.user_email}/session_files/{file.name}", chat_blob_name
                )
                blob_data = self.file_storage.download_blob(chat_blob_name)
                # Create a part with the file content
                blob_dict = BlobDict(mime_type=file.mime_type, data=blob_data)
                parts.append(blob_dict)
            content = ContentDict(role="user", parts=parts)
            chat_session.history.append(
                ChatMessage(author="user", content=message.content, files=files)
            )
            self._log.debug("Sending message: %s", content)
            responses = chat.send_message_streaming(content)
            for response in responses:
                self._log.debug("Received response: %s", response)
                if response.text:
                    yield StreamedEvent(type="text", value=response.text)
                # await asyncio.sleep(0.1)
            out_message = ChatMessage.from_content(chat.get_history()[-1], file_names)
            chat_session.history.append(out_message)
            if not chat_session.summary:
                chat_session.summary = chat_session.history[0].content
            self.storage.save(chat_session)
        except Exception as e:
            self._log.exception("Error in get_answer_async: %s", e)
            yield StreamedEvent(type=f"error:{type(e).__name__}", value=str(e))

    async def get_context(self, text: str, agent: Agent = None) -> str:
        """Get the context of the chat session."""
        if agent:
            context = agent.system_prompt + "\n\n"
            keywords = agent.keywords
        elif self.role:
            context = self.role + "\n\n"
            keywords = None
        else:
            context = ""
            keywords = None
        neartest = await self.knowledge_base_storage.find_nearest(f"{text}", keywords)
        for n in neartest:
            context += "\n\n# " + n.title + "\n" + n.content + "\n\n"
        return context

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

    def get(self, chat_session_id: str, user: str) -> ChatSession:
        """Get chat history by id."""
        if chat_session_id == "_NEW_":
            chat_session = ChatSession(user=user)
        else:
            chat_session = self.storage.get(chat_session_id)
            if chat_session and chat_session.user != user:
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
        if not chat_session:
            self._log.warning("Chat session not found: %s", chat_session_id)
            return
        if chat_session.user != user:
            raise ChatSessionUserError()
        chat_session = self.storage.get(chat_session_id)
        for message in chat_session.history:
            for file in message.files:
                try:
                    self.file_storage.delete(file.name)
                except exceptions.NotFound:
                    pass
        return self.storage.delete(chat_session_id)
