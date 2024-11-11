"""This module contains dependencies for FastAPI endpoints."""

import os
from typing import Annotated
from dotenv import load_dotenv
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from ampf.auth import TokenPayload, AuthService, InsufficientPermissionsError
from ampf.base import AmpfBaseFactory, BaseEmailSender, SmtpEmailSender
from ampf.gcp import AmpfGcpFactory
from app.user.user_model import User
from app.user.user_service import UserService
from gcp import FileStorage

from app.config import ServerConfig
from app.agent import AgentService
from app.chat import ChatService


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


def get_email_sender(conf: ServerConfigDep) -> BaseEmailSender:
    return SmtpEmailSender(**dict(conf.smtp))


EmailSenderDep = Annotated[BaseEmailSender, Depends(get_email_sender)]


def auth_service_dep(
    factory: FactoryDep,
    email_sender: EmailSenderDep,
    conf: ServerConfigDep,
    user_service: UserServceDep,
) -> AuthService:
    default_user = User(**dict(conf.default_user))
    return AuthService(
        storage_factory=factory,
        email_sender=email_sender,
        user_service=user_service,
        default_user=default_user,
        jwt_secret_key=conf.jwt_secret_key,
    )


AuthServiceDep = Annotated[AuthService, Depends(auth_service_dep)]


def decode_token(auth_service: AuthServiceDep, token: AuthTokenDep):
    return auth_service.decode_token(token)


TokenPayloadDep = Annotated[TokenPayload, Depends(decode_token)]

def get_user_email(token_payload: TokenPayloadDep) -> str:
    """Returns the current user's ID from the session."""
    return token_payload.email


UserEmailDep = Annotated[str, Depends(get_user_email)]

class Authorize:
    """Dependency for authorizing users based on their role."""

    def __init__(self, required_role: str = None):
        self.required_role = required_role

    def __call__(self, token_payload: TokenPayloadDep) -> bool:
        if not self.required_role or self.required_role in token_payload.roles:
            return True
        else:
            raise InsufficientPermissionsError()


def get_agent_service(config: ServerConfigDep, factory: FactoryDep) -> AgentService:
    return AgentService(config, factory)


AgentServiceDep = Annotated[AgentService, Depends(get_agent_service)]


def get_chat_service(
    factory: FactoryDep, server_config: ServerConfigDep
) -> ChatService:
    return ChatService(factory, file_storage, server_config)


ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]
