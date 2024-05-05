import unittest

from vertexai.generative_models import GenerativeModel, ChatSession, Content, Part
from verrtex_ai.vertex_ai_factory import VertexAiFactory


class TestVertexAiFactory(unittest.TestCase):
    def test_get_model(self):
        factory = VertexAiFactory()
        model = factory.get_model()
        self.assertIsInstance(model, GenerativeModel)

    def test_get_chat(self):
        factory = VertexAiFactory()
        chat = factory.get_chat()
        self.assertIsInstance(chat, ChatSession)

    def test_get_chat_with_history(self):
        factory = VertexAiFactory()
        history = [
            Content(role="user", parts=[Part.from_text("Hello")]),
            Content(role="model", parts=[Part.from_text("Hi")]),
            Content(role="user", parts=[Part.from_text("How are you?")]),
        ]
        chat = factory.get_chat(history)
        self.assertIsInstance(chat, ChatSession)

    def test_send_message(self):
        factory = VertexAiFactory()
        chat = factory.get_chat()
        resp = chat.send_message("Who was the first president of the United States?")
        self.assertIsInstance(chat.history, list)
        self.assertIsInstance(chat.history[0], Content)
        self.assertIsInstance(resp.text, str)


if __name__ == "__main__":
    unittest.main()
