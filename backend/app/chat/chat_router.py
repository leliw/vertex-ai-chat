from fastapi import APIRouter, Request

from .chat_model import ChatSessionHeader


class ChatRouter:
    def __init__(self, chat_service):
        self.chat_service = chat_service

        self.router = APIRouter(prefix="/chats", tags=["chat sessions"])
        self.router.get("", response_model=list[ChatSessionHeader])(self.get_all)

    async def get_all(self, request: Request) -> list[ChatSessionHeader]:
        return await self.chat_service.get_all(request.state.session_data.user.email)
