import datetime
import pytest
from app.agent.agent_model import Agent
from app.chat.chat_model import ChatSession
from app.chat.chat_service import ChatHistoryException, ChatService
from app.chat.message.message_model import ChatMessage
from gcp.gcp_file_storage import FileStorage

model_name = "gemini-1.5-flash"


@pytest.fixture
def chat_service():
    file_storage = FileStorage("vertex-ai-chat-dev-session-files")
    service = ChatService(file_storage)
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
    try:
        for p in chat_service.get_answer_async(
            model_name=model_name, chat_session=session, message=message, files=[]
        ):
            text += p.value
    except ChatHistoryException as e:
        chat_history = e.chat_session.history
    answer = ChatMessage(author="ai", content=text)
    assert answer.author == "ai"
    assert isinstance(answer.content, str)
    assert chat_history[0] == message
    assert chat_history[1] == answer


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
