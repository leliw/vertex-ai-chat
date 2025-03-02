import logging
from fastapi import APIRouter

from ampf.base import KeyNotExistsException
from ampf.fastapi import JsonStreamingResponse

from app.chat.chat_model import ChatSession
from app.dependencies import (
    ServerConfigDep,
    AgentServiceDep,
    ChatServiceDep,
    UserEmailDep,
    FileServiceDep,
)
from app.chat.message.message_model import ChatMessage, ChatMessageFile


router = APIRouter(
    tags=["Chat message"],
)

_log = logging.getLogger(__name__)


@router.post("", responses={200: {"content": {"text/event-stream": {}}}})
async def post_message_async(
    message: ChatMessage,
    config: ServerConfigDep,
    user_email: UserEmailDep,
    agent_service: AgentServiceDep,
    chat_service: ChatServiceDep,
    file_service: FileServiceDep,
    chat_id: str,
    model: str = None,
    agent: str = None,
):
    """Post message to chat and return async response"""
    try:
        chat_session = chat_service.get(chat_id, user_email)
    except KeyNotExistsException:
        chat_session = None
    if not chat_session:
        chat_session = ChatSession(chat_session_id=chat_id, user=user_email)
    files: list[ChatMessageFile] = [
        ChatMessageFile(**sf.model_dump()) for sf in file_service.get_all_files()
    ]
    if agent:
        agent_obj = agent_service.get(user_email, agent)
    else:
        agent_obj = agent_service.create_default(
            user_email, ai_model_name=model if model else config.default_model
        )
    return JsonStreamingResponse(
        chat_service.get_answer_async(
            agent=agent_obj,
            chat_session=chat_session,
            message=message,
            files=files,
        ),
    )
