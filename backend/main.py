"""Main file for FastAPI server"""

import os
from typing import List, Optional
from dotenv import load_dotenv
from fastapi import FastAPI, File, Request, Response, UploadFile
from fastapi.responses import HTMLResponse, StreamingResponse


from base import static_file_response
from gcp import SessionManager, SessionData as BaseSessionData, FileStorage

from app.config import config
from app.knowledge_base import KnowledgeBaseRouter

from chat_service import (
    ChatHistoryException,
    ChatMessageFile,
    ChatService,
    ChatMessage,
    ChatSession,
    ChatSessionHeader,
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
    return session_manager.auth(request, response)


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


chat_service = ChatService(file_storage)


@app.get("/api/models")
def models_get_all() -> list[str]:
    return [m.strip() for m in config.get("models").split(",")]


@app.get("/api/chats", tags=["chat sessions"])
async def chat_get_all(request: Request) -> list[ChatSessionHeader]:
    return await chat_service.get_all(request.state.session_data.user.email)


@app.get("/api/chats/{chat_id}", tags=["chat sessions"])
async def chat_get_by_id(chat_id: str, request: Request) -> ChatSession:
    chat_session = await chat_service.get_chat(
        chat_id, request.state.session_data.user.email
    )
    request.state.session_data.chat_session = chat_session
    request.state.session_data.files = []
    return chat_session


@app.post("/api/chats/message", tags=["chat sessions"])
def chat_post_message_async(model: str, message: ChatMessage, request: Request):
    """Post message to chat and return async response"""
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
    responses = chat_service.get_answer_async(
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
            session_data.chat_session = e.chat_session
            session_data.files = []
            await session_manager.update_session(request, session_data)
            if e.exception:
                raise e.exception

    return StreamingResponse(
        handle_history(responses),
        media_type="text/event-stream",
    )


@app.put("/api/chats/{chat_session_id}", tags=["chat sessions"])
async def chat_session_update(
    chat_session_id: str,
    chat_session: ChatSession,
    request: Request,
):
    """Update chat session."""
    message_index = len(chat_session.history)
    files = request.state.session_data.chat_session.history[message_index].files
    request.state.session_data.chat_session = chat_session
    request.state.session_data.files = files
    for file in files:
        file.url = "/".join(file.url.split("/")[-2:])
    await chat_service.update_chat(
        chat_session_id, chat_session, request.state.session_data.user.email
    )


@app.delete("/api/chats/{chat_id}", tags=["chat sessions"])
async def chat_delete(chat_id: str, request: Request) -> None:
    await chat_service.delete_chat(chat_id, request.state.session_data.user.email)


@app.post("/api/files", tags=["files"])
def files_post(request: Request, files: List[UploadFile] = File(...)):
    for file in files:
        request.state.session_data.upload_file(file)


@app.delete("/api/files/{name}", tags=["files"])
def files_delete(name: str, request: Request):
    request.state.session_data.delete_file(name)


knowledge_base_router = KnowledgeBaseRouter()
app.include_router(knowledge_base_router.router, prefix="/api")


# Angular static files - it have to be at the end of file
@app.get("/{full_path:path}", response_class=HTMLResponse, tags=["static"])
async def catch_all(_: Request, full_path: str):
    """Catch all for Angular routing"""
    return static_file_response("static/browser", full_path)
