"""Main file for FastAPI server"""

import datetime
import os
from typing import Annotated, Optional
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request, Response
from fastapi.responses import HTMLResponse, StreamingResponse
from pyaml_env import parse_config

from gcp_oauth import OAuth
from gcp_session import SessionManager, SessionData as BaseSessionData
from static_files import static_file_response

from chat_service import (
    ChatHistoryException,
    ChatService,
    ChatMessage,
    ChatSession,
    ChatSessionHeader,
)


class SessionData(BaseSessionData):
    login_time: Optional[datetime.datetime] = None
    chat_session: Optional[ChatSession] = None


load_dotenv()
app = FastAPI()
config: dict = parse_config("./config.yaml")
config["oauth_client_id"] = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
oAuth = OAuth()
session_manager = SessionManager[SessionData](oAuth, SessionData)


@app.get("/login")
async def login_google(request: Request):
    return oAuth.redirect_login(request)


@app.get("/auth")
async def auth_google(code: str, response: Response):
    user_data = await oAuth.auth(code)
    await session_manager.create_session(response, SessionData(user=user_data))
    return user_data


SessionDataDep = Annotated[SessionData, Depends(session_manager.session_reader)]


@app.get("/api/user")
async def user_get(session_data: SessionDataDep):
    return session_data.user


@app.get("/api/config")
async def read_config():
    """Return config from yaml file"""
    return config


chat_service = ChatService()


@app.get("/api/models")
def models_get_all() -> list[str]:
    return [m.strip() for m in config.get("models").split(",")]


@app.get("/api/chat")
async def chat_get_all(session_data: SessionDataDep) -> list[ChatSessionHeader]:
    return await chat_service.get_all(session_data.user.email)


@app.get("/api/chat/{chat_id}")
async def chat_get_by_id(
    chat_id: str, request: Request, session_data: SessionDataDep
) -> ChatSession:
    chat_session = await chat_service.get_chat(chat_id, session_data.user.email)
    session_data.chat_session = chat_session
    await session_manager.update_session(request, session_data)
    return session_data.chat_session


@app.post("/api/chat/message")
def chat_post_message_async(
    message: ChatMessage, request: Request, session_data: SessionDataDep
):
    """Post message to chat and return async response"""
    responses = chat_service.get_answer_async(
        chat_session=session_data.chat_session,
        message=message,
    )

    async def handle_history(responses):
        try:
            for i, r in enumerate(responses):
                comma = "," if i > 0 else ""
                yield f"{comma}{r.model_dump_json()}\n"
        except ChatHistoryException as e:
            session_data.chat_session = e.chat_session
            await session_manager.update_session(request, session_data)

    return StreamingResponse(
        handle_history(responses),
        media_type="text/event-stream",
    )


@app.put("/api/chat/{chat_session_id}")
async def chat_session_update(
    chat_session_id: str,
    chat_session: ChatSession,
    request: Request,
    session_data: SessionDataDep,
):
    """Update chat session."""
    session_data.chat_session = chat_session
    await session_manager.update_session(request, session_data)
    await chat_service.update_chat(
        chat_session_id, chat_session, session_data.user.email
    )


@app.delete("/api/chat/{chat_id}")
async def chat_delete(chat_id: str, session_data: SessionDataDep) -> None:
    await chat_service.delete_chat(chat_id, session_data.user.email)


# Angular static files - it have to be at the end of file
@app.get("/{full_path:path}", response_class=HTMLResponse)
async def catch_all(_: Request, full_path: str):
    """Catch all for Angular routing"""
    return static_file_response("static/browser", full_path)
