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
    ChatSessionHeader,
)


class SessionData(BaseSessionData):
    login_time: Optional[datetime.datetime] = None
    chat_session_id: Optional[str] = None
    chat_history: Optional[list[ChatMessage]] = []


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


@app.get("/api/chat")
async def chat_get_all(session_data: SessionDataDep) -> list[ChatSessionHeader]:
    return await chat_service.get_all(session_data.user.email)


@app.get("/api/chat/{chat_id}")
async def chat_get_by_id(
    chat_id: str, request: Request, session_data: SessionDataDep
) -> list[ChatMessage]:
    if chat_id == "_NEW_":
        # Create new chat
        session_data.chat_session_id = None
        session_data.chat_history = []
    else:
        # Load chat
        session_data.chat_history = await chat_service.get_chat(
            chat_id, session_data.user.email
        )
    await session_manager.update_session(request, session_data)
    return session_data.chat_history


@app.post("/api/chat")
async def chat_post(
    message: ChatMessage, request: Request, session_data: SessionDataDep
):
    """Post message to chat"""
    answer, session_data.chat_history = chat_service.get_answer(
        history=session_data.chat_history, message=message
    )
    await session_manager.update_session(request, session_data)
    return answer


@app.post("/api/chat/async")
def chat_post_async(
    message: ChatMessage, request: Request, session_data: SessionDataDep
):
    """Post message to chat and return async response"""
    chat_session_id = session_data.chat_session_id
    user_email = session_data.user.email
    history = session_data.chat_history
    responses = chat_service.get_answer_async(
        history=history,
        message=message,
        chat_session_id=chat_session_id,
        user=user_email,
    )

    async def handle_history(responses):
        try:
            for r in responses:
                yield r
        except ChatHistoryException as e:
            session_data.chat_session_id = e.chat_session_id
            session_data.chat_history = e.history
            await session_manager.update_session(request, session_data)

    return StreamingResponse(
        handle_history(responses),
        media_type="text/event-stream",
    )


@app.delete("/api/chat/{chat_id}")
async def chat_delete(chat_id: str, session_data: SessionDataDep) -> None:
    await chat_service.delete_chat(chat_id, session_data.user.email)


# Angular static files - it have to be at the end of file
@app.get("/{full_path:path}", response_class=HTMLResponse)
async def catch_all(_: Request, full_path: str):
    """Catch all for Angular routing"""
    return static_file_response("static/browser", full_path)
