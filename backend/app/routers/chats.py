from fastapi import APIRouter

from app.chat.chat_model import ChatSession, ChatSessionHeader
from app.dependencies import ChatServiceDep, UserEmailDep
from app.routers import chats_message


router = APIRouter(tags=["chat sessions"])
router.include_router(prefix="/{chat_id}/messages", router=chats_message.router)  # fmt: skip
ID_PATH = "/{chat_id}"


@router.get("")
async def get_all(
    service: ChatServiceDep, user_email: UserEmailDep
) -> list[ChatSessionHeader]:
    return await service.get_all(user_email)


@router.get(ID_PATH)
async def get(
    service: ChatServiceDep, user_email: UserEmailDep, chat_id: str
) -> ChatSession:
    chat_session = service.get(chat_id, user_email)
    return chat_session


@router.put(ID_PATH)
async def chat_session_update(
    service: ChatServiceDep,
    user_email: UserEmailDep,
    chat_id: str,
    chat_session: ChatSession,
):
    """Update chat session."""
    await service.update_chat(chat_id, chat_session, user_email)


@router.delete(ID_PATH)
async def chat_delete(
    service: ChatServiceDep, chat_id: str, user_email: UserEmailDep
) -> None:
    await service.delete_chat(chat_id, user_email)
