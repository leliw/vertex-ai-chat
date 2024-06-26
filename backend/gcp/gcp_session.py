from datetime import datetime
from typing import Optional, Type, TypeVar
from uuid import uuid4
from fastapi import HTTPException, Request, Response, UploadFile
from fastapi.responses import JSONResponse
from fastapi_sessions.backends.session_backend import SessionBackend
from pydantic import BaseModel, Field, PrivateAttr

from base import InvalidSessionException, BasicSessionManager
from base.session_manager import BasicSessionBackend

from .gcp_file_storage import FileStorage
from .gcp_storage import Storage
from .gcp_oauth import OAuth, UserData


class SessionFile(BaseModel):
    name: str
    url: Optional[str] = None
    mime_type: str


class SessionData(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)
    user: Optional[UserData] = None
    files: list[SessionFile] = Field(default_factory=list)

    _session_manager: BasicSessionManager = PrivateAttr(default=None)

    def upload_file(self, file: UploadFile):
        self._session_manager.upload_file(self.session_id, file)
        session_file = SessionFile(name=file.filename, mime_type=file.content_type)
        self.files.append(session_file)

    def delete_file(self, name: str):
        file = next((f for f in self.files if f.name == name), None)
        self._session_manager.delete_file(self.session_id, file)
        self.files = [f for f in self.files if f.name != name]

    async def update_session(self, request: Request):
        await self._session_manager.update_session(request, self)

    async def delete_session(self, request: Request, response: Response):
        await self._session_manager.delete_session(
            request, response, session_id=self.session_id
        )


SessionModel = TypeVar("SessionModel", bound=SessionData)


class SessionManager(BasicSessionManager[SessionModel]):
    """Session manager for GCP."""

    def __init__(
        self,
        o_auth: OAuth = None,
        backend: SessionBackend = None,
        session_class: Type[SessionModel] = SessionData,
        file_storage: FileStorage = None,
    ):
        if not backend:
            storage = Storage("sessions", session_class)
            backend = BasicSessionBackend(storage, session_class)
        super().__init__(backend=backend)
        self.o_auth = o_auth or OAuth()
        self.session_class = session_class
        self.file_storage = file_storage

    def redirect_login(self, request):
        return self.o_auth.redirect_login(request)

    async def auth(self, request: Request, response: Response):
        code = request.query_params.get("code")
        user_data = await self.o_auth.auth(code)
        await self.create_session(response, SessionData(user=user_data))
        return user_data

    async def session_reader(
        self, request: Request, response: Response
    ) -> SessionModel:
        try:
            data = await self.__call__(request)
            return data
        except InvalidSessionException:
            pass
        except HTTPException as e:
            if e.status_code != 403 or e.detail != "No session provided":
                raise e
        user_data = self.o_auth.verify_token(request)
        if not user_data:
            raise HTTPException(status_code=401, detail="Unauthorized")
        data = self.create_session_for_user(user_data)
        await self.create_session(request, response, data)
        return data

    def create_session_for_user(self, user_data: UserData) -> SessionModel:
        return self.session_class(user=user_data)

    async def middleware_add_session_data(self, request: Request, call_next):
        """Middleware to add session data to request."""
        try:
            session_in = await self.get_session(request)
            if not session_in:
                raise InvalidSessionException()
            if session_in.user is None and self.o_auth.requre_auth(request):
                raise InvalidSessionException()
            request.state.session_data = session_in.model_copy(deep=True)
        except (InvalidSessionException, HTTPException):
            session_in = None
            if self.o_auth.requre_auth(request):
                user_data = self.o_auth.verify_token(request)
                if not user_data:
                    return JSONResponse(status_code=401, content={'reason': "Unauthorized"})
            else:
                user_data = None
            request.state.session_data = self.create_session_for_user(user_data)
        request.state.session_data._session_manager = self
        response = await call_next(request)
        request.state.session_data._session_manager = None
        session_out = request.state.session_data.model_copy(deep=True)
        request.state.session_data._session_manager = self
        if session_in != session_out:
            if not session_in:
                await self.create_session(request, response, session_out)
            else:
                await self.update_session(request, session_out)
        return response

    def upload_file(self, session_id: str, file: UploadFile):
        blob_name = f"session-{session_id}/{file.filename}"
        self.file_storage.upload_blob_from_file(blob_name, file)

    def delete_file(self, session_id: str, file: SessionFile):
        blob_name = f"session-{session_id}/{file.name}"
        self.file_storage.delete(blob_name)

    async def delete_session(
        self, request: Request, response: Response, session_id: str = None
    ):
        session_id = session_id or request.state.session_data.session_id
        blob_name = f"session-{session_id}"
        self.file_storage.delete_folder(blob_name)
        await super().delete_session(request, response)
