from typing import Generic, Type
from fastapi import HTTPException, Request, Response
from uuid import UUID, uuid4

from fastapi_sessions.backends.implementations import InMemoryBackend
from fastapi_sessions.session_verifier import SessionVerifier
from fastapi_sessions.frontends.implementations import SessionCookie, CookieParameters
from fastapi_sessions.backends.session_backend import (
    SessionBackend,
    BackendError,
    SessionModel,
)

from ampf.base.base_storage import BaseStorage


class InvalidSessionException(HTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="Invalid session")


class BasicSessionBackend(Generic[SessionModel], SessionBackend[UUID, SessionModel]):
    def __init__(self, storage: BaseStorage, session_class: Type[SessionModel]) -> None:
        """Initialize a new in-memory database."""
        self.storage = storage
        self.session_class = session_class

    async def create(self, session_id: UUID, data: SessionModel):
        """Create a new session entry."""
        if self.storage.get(str(session_id)):
            raise BackendError("create can't overwrite an existing session")
        self.storage.put(str(session_id), data)

    async def read(self, session_id: UUID):
        """Read an existing session data."""
        data = self.storage.get(str(session_id))
        if not data:
            return
        return data

    async def update(self, session_id: UUID, data: SessionModel) -> None:
        """Update an existing session."""
        if self.storage.get(str(session_id)):
            self.storage.put(str(session_id), data)
        else:
            raise BackendError("session does not exist, cannot update")

    async def delete(self, session_id: UUID) -> None:
        """Delete an existing session."""
        self.storage.delete(str(session_id))


class BasicVerifier(SessionVerifier[UUID, SessionModel]):
    def __init__(
        self,
        *,
        identifier: str,
        auto_error: bool,
        backend: SessionBackend[UUID, SessionModel],
        auth_http_exception: HTTPException,
    ):
        self._identifier = identifier
        self._auto_error = auto_error
        self._backend = backend
        self._auth_http_exception = auth_http_exception

    @property
    def identifier(self):
        return self._identifier

    @property
    def backend(self):
        return self._backend

    @property
    def auto_error(self):
        return self._auto_error

    @property
    def auth_http_exception(self):
        return self._auth_http_exception

    def verify_session(self, model: SessionModel) -> bool:
        """If the session exists, it is valid"""
        return True


class BasicSessionManager(Generic[SessionModel]):
    """Session manager."""

    def __init__(
        self, backend: SessionBackend = None, verifier: SessionVerifier = None
    ):
        self.backend = backend or InMemoryBackend[UUID, SessionModel]()
        self.verifier = verifier or BasicVerifier(
            identifier="general_verifier",
            auto_error=True,
            backend=self.backend,
            auth_http_exception=InvalidSessionException(),
        )
        cookie_params = CookieParameters()
        self.cookie = SessionCookie(
            cookie_name="session_id",
            identifier="general_verifier",
            auto_error=True,
            secret_key="DONOTUSE",
            cookie_params=cookie_params,
        )

    async def create_session(
        self, request: Request, response: Response, data: SessionModel
    ):
        """Create a new session and attach it to the response and
        to the request (if it wasn't already attached)."""
        if hasattr(data, "session_id") and data.session_id:
            # If the session model has a session_id attribute, use it
            session_id = UUID(data.session_id)
        else:
            session_id = uuid4()
        await self.backend.create(session_id, data)
        self.cookie.attach_to_response(response, session_id)
        request.cookies[self.cookie.model.name] = str(
            self.cookie.signer.dumps(session_id.hex)
        )
        return session_id

    def get_session_id(self, request: Request) -> UUID:
        """Get the session id from the request."""
        return self.cookie(request)

    async def get_session(self, request: Request) -> SessionModel:
        """Get the current session, if any"""
        self.cookie(request)
        return await self.verifier(request)

    async def update_session(self, request: Request, data: SessionModel):
        """Update the current session."""
        session_id = self.cookie(request)
        await self.backend.update(session_id, data)

    async def delete_session(self, request: Request, response: Response):
        """Delete the current session."""
        session_id = self.cookie(request)
        await self.backend.delete(session_id)
        self.cookie.delete_from_response(response)

    async def __call__(self, request: Request) -> SessionModel:
        """Get the current session, if any"""
        return await self.get_session(request)
