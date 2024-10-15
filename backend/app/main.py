"""Main file for FastAPI server"""

from typing import List, Optional

from fastapi import FastAPI, File, Request, Response, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse

from app.chat.chat_service import ChatSession
from app.routers import chats, chats_message
from app.user import User
from base import static_file_response
from gcp import SessionManager, SessionData as BaseSessionData

from app.dependencies import ConfigDep, file_storage
from .routers import users, agents, knowledge_base


class SessionData(BaseSessionData):
    chat_session: Optional[ChatSession] = None
    api_user: Optional[User] = None


app = FastAPI()
session_manager = SessionManager(session_class=SessionData, file_storage=file_storage)


@app.middleware("http")
async def add_session_data(request: Request, call_next):
    return await session_manager.middleware_add_session_data(request, call_next)


@app.get("/api/login")
async def login_google(request: Request):
    return session_manager.redirect_login(request)


app.include_router(chats.router, prefix="/api/chats")
app.include_router(users.router, prefix="/api")


@app.get("/api/auth")
async def auth_google(user_service: users.UserServiceDep, request: Request, response: Response):
    user_data = await session_manager.auth(request, response)
    if user_data:
        user = user_service.get(user_data["email"])
        if user:
            return JSONResponse(status_code=200, content=user_data)
        else:
            return JSONResponse(status_code=404, content=user_data)


@app.post("/api/logout")
async def logout(request: Request, response: Response):
    await request.state.session_data.delete_session(request, response)


@app.get("/api/user")
async def user_get(user_service: users.UserServiceDep, request: Request):
    if not request.state.session_data.api_user:
        request.state.session_data.api_user = user_service.get(
            request.state.session_data.user.email
        )
    return request.state.session_data.api_user


@app.get("/api/config")
async def read_config(config: ConfigDep):
    """Return config from yaml file"""
    return config


@app.get("/api/ping")
def ping():
    """Just for keep container alive"""


@app.get("/api/models")
def models_get_all(config: ConfigDep) -> list[str]:
    return [m.strip() for m in config.get("models").split(",")]


@app.post("/api/files", tags=["files"])
def files_post(request: Request, files: List[UploadFile] = File(...)):
    for file in files:
        request.state.session_data.upload_file(file)


@app.delete("/api/files/{name}", tags=["files"])
def files_delete(name: str, request: Request):
    request.state.session_data.delete_file(name)


app.include_router(agents.router, prefix="/api/agents")
app.include_router(knowledge_base.router, prefix="/api/knowledge-base")
app.include_router(chats_message.router, prefix="/api/chats/message")


# Angular static files - it have to be at the end of file
@app.get("/{full_path:path}", response_class=HTMLResponse, tags=["static"])
async def catch_all(_: Request, full_path: str):
    """Catch all for Angular routing"""
    return static_file_response("static/browser", full_path)
