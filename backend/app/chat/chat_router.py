from fastapi import APIRouter, Request

from .chat_model import ChatSession, ChatSessionHeader


class ChatRouter:
    def __init__(self, chat_service):
        self.service = chat_service

        ID_PATH = "/{chat_id}"
        self.router = APIRouter(prefix="/chats", tags=["chat sessions"])
        self.router.get("", response_model=list[ChatSessionHeader])(self.get_all)
        self.router.get(ID_PATH, response_model=ChatSession)(self.get)
        self.router.put(ID_PATH)(self.chat_session_update)
        self.router.delete(ID_PATH)(self.chat_delete)

    async def get_all(self, request: Request) -> list[ChatSessionHeader]:
        return await self.service.get_all(request.state.session_data.user.email)

    async def get(self, chat_id: str, request: Request) -> ChatSession:
        chat_session = await self.service.get_chat(
            chat_id, request.state.session_data.user.email
        )
        request.state.session_data.chat_session = chat_session
        request.state.session_data.files = []
        return chat_session

    async def chat_session_update(
        self,
        chat_id: str,
        chat_session: ChatSession,
        request: Request,
    ):
        """Update chat session."""
        message_index = len(chat_session.history)
        files = request.state.session_data.chat_session.history[message_index].files
        request.state.session_data.chat_session = chat_session
        request.state.session_data.files = files
        for file in files:
            file.url = "/".join(file.url.split("/")[-2:])
        await self.service.update_chat(
            chat_id, chat_session, request.state.session_data.user.email
        )

    async def chat_delete(self, chat_id: str, request: Request) -> None:
        await self.service.delete_chat(chat_id, request.state.session_data.user.email)
