import datetime
from io import BytesIO
from fastapi import UploadFile
import pytest
from app.file.file_service import FileService
from haintech.ai import AiFactory
from ampf.gcp import GcpFactory
from app.agent.agent_model import Agent
from app.chat.chat_model import ChatSession
from app.chat.chat_service import ChatService
from app.chat.message.message_model import ChatMessage, ChatMessageFile
from app.config import ServerConfig
from tests.conftest import MockAITextEmbeddingModel

ai_model_name = "gemini-1.5-flash"


@pytest.fixture
def factory(test_config):
    GcpFactory.init_client(test_config.file_storage_bucket)
    return GcpFactory()


@pytest.fixture
def ai_factory():
    return AiFactory()


@pytest.fixture
def chat_service(
    test_config: ServerConfig,
    factory: GcpFactory,
    ai_factory: AiFactory,
    embedding_model: MockAITextEmbeddingModel,
    user_email: str,
):
    file_storage = factory.create_blob_storage(f"users/{user_email}/session_files")
    service = ChatService(
        factory, ai_factory, embedding_model, file_storage, ServerConfig(), user_email
    )
    service.role = "This is role"
    return service


@pytest.fixture
def file_service(
    test_config: ServerConfig, factory: GcpFactory, user_email: str
) -> FileService:
    return FileService(test_config, factory, user_email)


def test_get_answer(chat_service: ChatService):
    history = []
    message = ChatMessage(author="user", content="Hello")

    answer, chat_history = chat_service.get_answer(ai_model_name, history, message)

    assert answer.author == "ai"
    assert isinstance(answer.content, str)
    assert chat_history[0] == message
    assert chat_history[1] == answer


@pytest.mark.asyncio
async def test_get_answer_async(chat_service: ChatService):
    session = ChatSession(
        chat_session_id="x",
        user="x",
        created=datetime.datetime.now(),
        history=[],
    )
    message = ChatMessage(author="user", content="Hello")
    text = ""
    async for p in chat_service.get_answer_async(
        ai_model_name=ai_model_name, chat_session=session, message=message, files=[]
    ):
        text += p.value
    answer = ChatMessage(author="ai", content=text)
    assert answer.author == "ai"
    assert isinstance(answer.content, str)


@pytest.mark.asyncio
async def test_get_context_without_agent(chat_service: ChatService):
    context = await chat_service.get_context("test")

    assert context.startswith("This is role")


@pytest.mark.asyncio
async def test_get_context_with_agent(chat_service: ChatService):
    agent = Agent(
        name="test",
        ai_model_name="test_model",
        system_prompt="Agent prompt",
        keywords=["test"],
    )
    context = await chat_service.get_context("test", agent)

    assert context == "Agent prompt\n\n"


@pytest.mark.asyncio
async def test_get_answer_async_with_file(
    chat_service: ChatService, file_service: FileService
):
    # STEP:1

    # Given: Uploaded file
    file_service.upload_file(
        UploadFile(
            filename="test1.txt",
            file=BytesIO(b"This is an attachment content: 123"),
            headers={"content-type": "text/plain"},
        )
    )
    # Given: Empty chat session
    session = ChatSession(
        chat_session_id="x",
        user="x",
        created=datetime.datetime.now(),
        history=[],
    )
    # Given: User message
    message = ChatMessage(author="user", content="Hello. What is in the attachment?")
    # When: Get answer async
    text = ""
    async for p in chat_service.get_answer_async(
        ai_model_name=ai_model_name,
        chat_session=session,
        message=message,
        files=[
            ChatMessageFile(
                name="test1.txt",
                mime_type="text/plain",
            )
        ],
    ):
        text += p.value
    answer = ChatMessage(author="ai", content=text)
    # Then: Answer is returned
    assert answer.author == "ai"
    assert isinstance(answer.content, str)
    assert "123" in answer.content

    # STEP: 2
    # When: Chat session is read
    read_session = chat_service.get(session.chat_session_id, session.user)
    # Then: Messages are two
    assert len(read_session.history) == 2
    # Then: File is specified
    assert "test1.txt" in read_session.history[0].files[0].name
