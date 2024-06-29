"""Main file for FastAPI server"""

import os
from typing import List, Optional
from dotenv import load_dotenv
from fastapi import FastAPI, File, Request, Response, UploadFile
from fastapi.responses import HTMLResponse


from app.chat.chat_router import ChatRouter
from base import static_file_response
from gcp import SessionManager, SessionData as BaseSessionData, FileStorage

from app.config import config
from app.knowledge_base import KnowledgeBaseRouter

from app.chat.chat_service import (
    ChatService,
    ChatSession,
)


class SessionData(BaseSessionData):
    chat_session: Optional[ChatSession] = None


load_dotenv()
app = FastAPI()
config["oauth_client_id"] = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
file_storage = FileStorage(os.getenv("FILE_STORAGE_BUCKET"))
session_manager = SessionManager(session_class=SessionData, file_storage=file_storage)


@app.middleware("http")
async def add_session_data(request: Request, call_next):
    return await session_manager.middleware_add_session_data(request, call_next)


@app.get("/api/login")
async def login_google(request: Request):
    return session_manager.redirect_login(request)


@app.get("/api/auth")
async def auth_google(request: Request, response: Response):
    return await session_manager.auth(request, response)


@app.post("/api/logout")
async def logout(request: Request, response: Response):
    await request.state.session_data.delete_session(request, response)


@app.get("/api/user")
async def user_get(request: Request):
    return request.state.session_data.user


@app.get("/api/config")
async def read_config():
    """Return config from yaml file"""
    return config


@app.get("/api/ping")
def ping():
    """Just for keep container alive"""


@app.get("/api/models")
def models_get_all() -> list[str]:
    return [m.strip() for m in config.get("models").split(",")]


chat_service = ChatService(file_storage)
chat_router = ChatRouter(chat_service)
app.include_router(chat_router.router, prefix="/api/chats")


@app.post("/api/files", tags=["files"])
def files_post(request: Request, files: List[UploadFile] = File(...)):
    for file in files:
        request.state.session_data.upload_file(file)


@app.delete("/api/files/{name}", tags=["files"])
def files_delete(name: str, request: Request):
    request.state.session_data.delete_file(name)


knowledge_base_router = KnowledgeBaseRouter()
app.include_router(knowledge_base_router.router, prefix="/api/knowledge-base")


# Angular static files - it have to be at the end of file
@app.get("/{full_path:path}", response_class=HTMLResponse, tags=["static"])
async def catch_all(_: Request, full_path: str):
    """Catch all for Angular routing"""
    return static_file_response("static/browser", full_path)
