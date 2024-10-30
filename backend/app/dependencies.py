"""This module contains dependencies for FastAPI endpoints."""

import logging
import os
from typing import Annotated
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer

from ampf.auth.auth_model import TokenPayload
from ampf.auth.auth_service import AuthService
from ampf.base import AmpfBaseFactory
from ampf.gcp import AmpfGcpFactory
from app.user.user_model import User
from app.user.user_service import UserService
from gcp import FileStorage

from app.config import ServerConfig
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
        self._log = logging.getLogger(__name__)

    def __call__(self, user_id: UserEmailDep) -> bool:
        if user_id == "marcin.leliwa@gmail.com":
            return True
        else:
            self._log.warning(f"User {user_id} does not have the required role.")
            raise InsufficientPermissionsError()


load_dotenv()


def get_server_config() -> ServerConfig:
    return ServerConfig()


ServerConfigDep = Annotated[ServerConfig, Depends(get_server_config)]
file_storage = FileStorage(os.getenv("FILE_STORAGE_BUCKET"))


def get_factory() -> AmpfBaseFactory:
    return AmpfGcpFactory()


FactoryDep = Annotated[AmpfBaseFactory, Depends(get_factory)]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")
AuthTokenDep = Annotated[str, Depends(oauth2_scheme)]


def user_service_dep(factory: FactoryDep) -> UserService:
    return UserService(factory)


UserServceDep = Annotated[UserService, Depends(user_service_dep)]


def auth_service_dep(
    factory: FactoryDep, conf: ServerConfigDep, user_service: UserServceDep
) -> AuthService:
    default_user = User(**dict(conf.default_user))
    return AuthService(
        storage_factory=factory,
        user_service=user_service,
        default_user=default_user,
        jwt_secret_key=conf.jwt_secret_key,
    )


AuthServiceDep = Annotated[AuthService, Depends(auth_service_dep)]


def decode_token(auth_service: AuthServiceDep, token: AuthTokenDep):
    return auth_service.decode_token(token)


TokenPayloadDep = Annotated[TokenPayload, Depends(decode_token)]


def get_agent_service(config: ServerConfigDep, factory: FactoryDep) -> AgentService:
    return AgentService(config, factory)


AgentServiceDep = Annotated[AgentService, Depends(get_agent_service)]


def get_chat_service(
    factory: FactoryDep, server_config: ServerConfigDep
) -> ChatService:
    return ChatService(factory, file_storage, server_config)


ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]
