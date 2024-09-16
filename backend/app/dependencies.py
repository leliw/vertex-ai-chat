"""This module contains dependencies for FastAPI endpoints."""

import os
from typing import Annotated
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Request

from ampf.base import AmpfBaseFactory
from ampf.gcp import AmpfGcpFactory
from gcp import FileStorage

from app.config import config
from app.agent import AgentService
from app.chat import ChatService


class InsufficientPermissionsError(HTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="Insufficient permissions.")


def get_current_user_id(request: Request) -> str:
    """Returns the current user's ID from the session."""
    return request.state.session_data.user.email


UserEmailDep = Annotated[str, Depends(get_current_user_id)]


class Authorize:
    """Dependency for authorizing users based on their role."""

    def __init__(self, required_role: str):
        self.required_role = required_role

    def __call__(self, user_id: UserEmailDep) -> bool:
        if user_id == "marcin.leliwa@gmail.com":
            return True
        else:
            raise InsufficientPermissionsError()


load_dotenv()
config["oauth_client_id"] = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
ConfigDep = Annotated[dict, Depends(lambda: config)]
file_storage = FileStorage(os.getenv("FILE_STORAGE_BUCKET"))
chat_service = ChatService(file_storage)


def get_factory() -> AmpfBaseFactory:
    return AmpfGcpFactory()


FactoryDep = Annotated[AmpfBaseFactory, Depends(get_factory)]


def get_agent_service(config: ConfigDep, factory: FactoryDep) -> AgentService:
    return AgentService(config, factory)


AgentServiceDep = Annotated[AgentService, Depends(get_agent_service)]
ChatServiceDep = Annotated[ChatService, Depends(lambda: chat_service)]
