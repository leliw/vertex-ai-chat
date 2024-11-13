import logging
from typing import Iterator
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.chat.chat_model import ChatSession
from app.dependencies import (
    ServerConfigDep,
    AgentServiceDep,
    ChatServiceDep,
    UserEmailDep,
)
from app.chat.chat_service import StreamedEvent
from app.chat.message.message_model import ChatMessage


router = APIRouter(
    tags=["Chat message"],
)

_log = logging.getLogger(__name__)


@router.post("", responses={200: {"content": {"text/event-stream": {}}}})
def post_message_async(
    message: ChatMessage,
    config: ServerConfigDep,
    user_email: UserEmailDep,
    agent_service: AgentServiceDep,
    chat_service: ChatServiceDep,
    chat_id: str,
    model: str = None,
    agent: str = None,
):
    """Post message to chat and return async response"""
    chat_session = chat_service.get(chat_id, user_email)
    if not chat_session:
        chat_session = ChatSession(chat_session_id=chat_id, user=user_email)
    # session_id = chat_session.chat_session_id
    # files: list[ChatMessageFile] = [
    #     ChatMessageFile(
    #         name=sf.name,
    #         url=sf.url or f"session-{session_id}/{sf.name}",
    #         mime_type=sf.mime_type,
    #     )
    #     for sf in request.state.session_data.files
    # ]
    files = []
    if agent:
        agent_obj = agent_service.get(user_email, agent)
    else:
        agent_obj = agent_service.create_default(
            user_email, model_name=model if model else config.get("default_model")
        )
    responses = chat_service.get_answer_async(
        agent=agent_obj,
        chat_session=chat_session,
        message=message,
        files=files,
    )

    def handle_history(responses: Iterator[StreamedEvent]):
        for i, r in enumerate(responses):
            comma = "," if i > 0 else ""
            yield f"{comma}{r.model_dump_json()}\n"

    return StreamingResponse(
        handle_history(responses),
        media_type="text/event-stream",
    )
