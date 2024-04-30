"""Main file for FastAPI server"""

import datetime
from typing import Annotated, Optional
from fastapi import Depends, FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from pyaml_env import parse_config

from chat_service import ChatService, ChatMessage
from gcp_oauth import OAuth
from gcp_secrets import GcpSecrets
from gcp_session import SessionManager, SessionData as BaseSessionData
from static_files import static_file_response


class SessionData(BaseSessionData):
    login_time: Optional[datetime.datetime] = None
    chat_history: Optional[list[ChatMessage]] = []


app = FastAPI()
config = parse_config("./config.yaml")
secrets = GcpSecrets(config.get("project_id"))
client_secret = secrets.get_secret("oauth_client_secret")
oAuth = OAuth(config.get("oauth_client_id"), client_secret)
session_manager = SessionManager[SessionData](oAuth, SessionData)


@app.get("/login")
async def login_google(request: Request):
    return oAuth.redirect_login(request)


@app.get("/auth")
async def auth_google(code: str, response: Response):
    user_data = await oAuth.auth(code)
    print(user_data)
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


# Angular static files - it have to be at the end of file
@app.get("/{full_path:path}", response_class=HTMLResponse)
async def catch_all(_: Request, full_path: str):
    """Catch all for Angular routing"""
    return static_file_response("static/browser", full_path)
