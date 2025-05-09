"""This module contains dependencies for FastAPI endpoints."""

import logging
from typing import Annotated
from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.security import OAuth2PasswordBearer

from haintech.ai import AiFactory
from ampf.auth import TokenPayload, AuthService, InsufficientPermissionsError
from ampf.base import BaseFactory, BaseEmailSender, SmtpEmailSender, EmailTemplate
from ampf.gcp import GcpFactory
from app.file.file_service import FileService
from app.user.user_service import UserService

from app.config import ServerConfig
from app.agent import AgentService
from app.chat import ChatService
from haintech.ai.base.base_ai_text_embedding_model import BaseAITextEmbeddingModel


load_dotenv()
_log = logging.getLogger(__name__)
_server_config = ServerConfig()


@asynccontextmanager
async def lifespan(app: FastAPI):
    _log.debug("Starting up")
    AiFactory().init_client()
    GcpFactory.init_client(_server_config.file_storage_bucket)
    UserService(GcpFactory()).initialize_storage_with_user(_server_config.default_user)
    yield
    _log.debug("Shutting down")


async def get_server_config() -> ServerConfig:
    return _server_config


ServerConfigDep = Annotated[ServerConfig, Depends(get_server_config)]


async def get_factory() -> BaseFactory:
    return GcpFactory()


FactoryDep = Annotated[BaseFactory, Depends(get_factory)]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")
AuthTokenDep = Annotated[str, Depends(oauth2_scheme)]


async def user_service_dep(factory: FactoryDep) -> UserService:
    return UserService(factory)


UserServceDep = Annotated[UserService, Depends(user_service_dep)]


async def get_email_sender(conf: ServerConfigDep) -> BaseEmailSender:
    return SmtpEmailSender(**dict(conf.smtp))


EmailSenderServiceDep = Annotated[BaseEmailSender, Depends(get_email_sender)]


async def auth_service_dep(
    factory: FactoryDep,
    email_sender_service: EmailSenderServiceDep,
    server_config: ServerConfigDep,
    user_service: UserServceDep,
) -> AuthService:
    reset_mail_template = EmailTemplate(**dict(server_config.reset_password_mail))
    return AuthService(
        storage_factory=factory,
        email_sender_service=email_sender_service,
        user_service=user_service,
        reset_mail_template=reset_mail_template,
        auth_config=server_config.auth,
    )


AuthServiceDep = Annotated[AuthService, Depends(auth_service_dep)]


async def decode_token(auth_service: AuthServiceDep, token: AuthTokenDep):
    return auth_service.decode_token(token)


TokenPayloadDep = Annotated[TokenPayload, Depends(decode_token)]


async def get_user_email(token_payload: TokenPayloadDep) -> str:
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


async def get_agent_service(
    config: ServerConfigDep, factory: FactoryDep
) -> AgentService:
    return AgentService(config, factory)


AgentServiceDep = Annotated[AgentService, Depends(get_agent_service)]


async def get_file_service(
    config: ServerConfigDep, factory: FactoryDep, user_email: UserEmailDep
) -> FileService:
    return FileService(config, factory, user_email)


FileServiceDep = Annotated[FileService, Depends(get_file_service)]


async def get_ai_factory() -> AiFactory:
    return AiFactory()


AiFactoryDep = Annotated[AiFactory, Depends(get_ai_factory)]


async def get_ai_text_embedding_model(
    ai_factory: AiFactoryDep, config: ServerConfigDep
):
    return ai_factory.get_text_embedding_model(config.knowledge_base.embedding_model)


EmbeddingModelDep = Annotated[
    BaseAITextEmbeddingModel, Depends(get_ai_text_embedding_model)
]


async def get_chat_service(
    factory: FactoryDep,
    ai_factory: AiFactoryDep,
    embedding_model: EmbeddingModelDep,
    server_config: ServerConfigDep,
    file_service: FileServiceDep,
    user_email: UserEmailDep,
) -> ChatService:
    return ChatService(
        factory,
        ai_factory,
        embedding_model,
        file_service.storage,
        server_config,
        user_email,
    )


ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]
