from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.chat.chat_service import ChatHistoryException

from app.config import config
from ..chat_model import ChatMessage, ChatMessageFile


class MessageRouter:
    def __init__(self, chat_service):
        self.service = chat_service

        self.router = APIRouter(tags=["chat messages"])
        self.router.post("", responses={200: {"content": {"text/event-stream": {}}}})(
            self.post_message_async
        )

    def post_message_async(self, model: str, message: ChatMessage, request: Request):
        """Post message to chat and return async response"""
        print(request.state.session_data)
        chat_session = request.state.session_data.chat_session
        session_id = request.state.session_data.session_id
        files: list[ChatMessageFile] = [
            ChatMessageFile(
                name=sf.name,
                url=sf.url or f"session-{session_id}/{sf.name}",
                mime_type=sf.mime_type,
            )
            for sf in request.state.session_data.files
        ]
        if not model:
            model = config.get("default_model")
        responses = self.service.get_answer_async(
            model_name=model,
            chat_session=chat_session,
            message=message,
            files=files,
        )

        async def handle_history(responses):
            try:
                for i, r in enumerate(responses):
                    comma = "," if i > 0 else ""
                    yield f"{comma}{r.model_dump_json()}\n"
            except ChatHistoryException as e:
                session_data = request.state.session_data
                print(session_data)
                session_data.chat_session = e.chat_session
                session_data.files = []
                await session_data._session_manager.update_session(
                    request, session_data
                )
                if e.exception:
                    raise e.exception

        return StreamingResponse(
            handle_history(responses),
            media_type="text/event-stream",
        )
