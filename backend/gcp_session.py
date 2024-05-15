from typing import Type, TypeVar
from fastapi import HTTPException, Request, Response

from fastapi_sessions.backends.session_backend import SessionBackend
from pydantic import BaseModel
from gcp_oauth import OAuth, UserData
from session_manager import (
    InvalidSessionException,
    SessionManager as BaseSessionManager,
)


class SessionData(BaseModel):
    user: UserData


SessionModel = TypeVar("SessionModel", bound=SessionData)


class SessionManager(BaseSessionManager[SessionModel]):
    """Session manager for GCP."""

    def __init__(self, o_auth: OAuth, backend: SessionBackend = None, session_class: Type[SessionModel] = SessionData):
        super().__init__(backend=backend)
        self.o_auth = o_auth
        self.session_class = session_class

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
            request.state.session_data = session_in.model_copy()
        except InvalidSessionException:
            session_in = None
            user_data = self.o_auth.verify_token(request)
            request.state.session_data = self.create_session_for_user(user_data)
        response = await call_next(request)
        session_out = request.state.session_data
        if session_in != session_out:
            if not session_in:
                await self.create_session(request, response, session_out)
            else:
                await self.update_session(request, session_out)
        return response
