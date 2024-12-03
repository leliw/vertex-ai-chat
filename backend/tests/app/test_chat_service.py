import datetime
import pytest
from ai_model.ai_factory import AiFactory
from ampf.gcp.ampf_gcp_factory import AmpfGcpFactory
from app.agent.agent_model import Agent
from app.chat.chat_model import ChatSession
from app.chat.chat_service import ChatService
from app.chat.message.message_model import ChatMessage
from app.config import ServerConfig
from gcp.gcp_file_storage import FileStorage

model_name = "gemini-1.5-flash"


@pytest.fixture
def factory():
    return AmpfGcpFactory()


@pytest.fixture
def ai_factory():
    return AiFactory()


@pytest.fixture
def chat_service(factory, ai_factory):
    file_storage = FileStorage("vertex-ai-chat-dev-session-files")
    service = ChatService(factory, ai_factory, file_storage, ServerConfig())
    service.role = "This is role"
    return service


def test_get_answer(chat_service):
    history = []
    message = ChatMessage(author="user", content="Hello")

    answer, chat_history = chat_service.get_answer(model_name, history, message)

    assert answer.author == "ai"
    assert isinstance(answer.content, str)
    assert chat_history[0] == message
    assert chat_history[1] == answer


def test_get_answer_async(chat_service):
    session = ChatSession(
        chat_session_id="x",
        user="x",
        created=datetime.datetime.now(),
        history=[],
    )
    message = ChatMessage(author="user", content="Hello")
    text = ""
    for p in chat_service.get_answer_async(
        model_name=model_name, chat_session=session, message=message, files=[]
    ):
        text += p.value
    answer = ChatMessage(author="ai", content=text)
    assert answer.author == "ai"
    assert isinstance(answer.content, str)


def test_get_context_without_agent(chat_service):
    context = chat_service.get_context("test")

    assert context.startswith("This is role")


def test_get_context_with_agent(chat_service):
    agent = Agent(
        name="test",
        model_name="test_model",
        system_prompt="Agent prompt",
        keywords=["test"],
    )
    context = chat_service.get_context("test", agent)

    assert context == "Agent prompt\n\n"
