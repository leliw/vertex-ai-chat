import pytest
from vertexai.generative_models import GenerativeModel, ChatSession, Content, Part
from haintech.ai import AiFactory


@pytest.fixture
def ai_factory():
    return AiFactory()


model_name = "gemini-1.5-flash"


def test_get_model(ai_factory):
    model = ai_factory.get_model(model_name)
    assert isinstance(model, GenerativeModel)


def test_get_chat(ai_factory):
    chat = ai_factory.get_chat(model_name)
    assert isinstance(chat, ChatSession)


def test_get_chat_with_history(ai_factory):
    history = [
        Content(role="user", parts=[Part.from_text("Hello")]),
        Content(role="model", parts=[Part.from_text("Hi")]),
        Content(role="user", parts=[Part.from_text("How are you?")]),
    ]
    chat = ai_factory.get_chat(model_name, history)
    assert isinstance(chat, ChatSession)


def test_send_message(ai_factory):
    chat = ai_factory.get_chat(model_name)
    resp = chat.send_message("Who was the first president of the United States?")
    assert isinstance(chat.history, list)
    assert isinstance(chat.history[0], Content)
    assert isinstance(resp.text, str)


@pytest.mark.asyncio
async def test_get_embedding(ai_factory):
    # Given: TextEmbeddingModel
    m = ai_factory.get_text_embedding_model()
    # And: Some text
    text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    # When: Embedding is requested
    embedding = await m.get_embedding(text)
    # Then: Embedding is returned
    assert embedding is not None
    assert len(embedding) > 0
