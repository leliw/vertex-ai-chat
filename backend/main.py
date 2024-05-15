"""Main file for FastAPI server"""

import datetime
import os
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, StreamingResponse
from pyaml_env import parse_config

from gcp_oauth import OAuth
from gcp_session import SessionManager, SessionData as BaseSessionData
from gcp_storage import Storage
from session_manager import BasicSessionBackend
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
session_storage = Storage("sessions", SessionData)
session_backend = BasicSessionBackend(session_storage, SessionData)
session_manager = SessionManager(oAuth, session_backend, SessionData)


@app.middleware("http")
async def add_session_data(request: Request, call_next):
    return await session_manager.middleware_add_session_data(request, call_next)


@app.get("/login")
async def login_google(request: Request):
    return oAuth.redirect_login(request)


@app.get("/auth")
async def auth_google(code: str, response: Response):
    user_data = await oAuth.auth(code)
    await session_manager.create_session(response, SessionData(user=user_data))
    return user_data


@app.get("/api/user")
async def user_get(request: Request):
    return request.state.session_data.user


@app.get("/api/config")
async def read_config():
    """Return config from yaml file"""
    return config


chat_service = ChatService()


@app.get("/api/chat")
async def chat_get_all(request: Request) -> list[ChatSessionHeader]:
    return await chat_service.get_all(request.state.session_data.user.email)


@app.get("/api/chat/{chat_id}")
async def chat_get_by_id(chat_id: str, request: Request) -> ChatSession:
    chat_session = await chat_service.get_chat(
        chat_id, request.state.session_data.user.email
    )
    request.state.session_data.chat_session = chat_session
    return chat_session


@app.post("/api/chat/message")
def chat_post_message_async(message: ChatMessage, request: Request):
    """Post message to chat and return async response"""
    chat_session = request.state.session_data.chat_session
    responses = chat_service.get_answer_async(
        chat_session=chat_session,
        message=message,
    )

    async def handle_history(responses):
        try:
            for i, r in enumerate(responses):
                comma = "," if i > 0 else ""
                yield f"{comma}{r.model_dump_json()}\n"
        except ChatHistoryException as e:
            session_data = request.state.session_data
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
):
    """Update chat session."""
    request.state.session_data.chat_session = chat_session
    await chat_service.update_chat(
        chat_session_id, chat_session, request.state.session_data.user.email
    )


@app.delete("/api/chat/{chat_id}")
async def chat_delete(chat_id: str, request: Request) -> None:
    await chat_service.delete_chat(chat_id, request.state.session_data.user.email)


# Angular static files - it have to be at the end of file
@app.get("/{full_path:path}", response_class=HTMLResponse)
async def catch_all(_: Request, full_path: str):
    """Catch all for Angular routing"""
    return static_file_response("static/browser", full_path)
