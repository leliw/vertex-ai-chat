import unittest

import vertexai
from vertexai.generative_models import GenerativeModel, ChatSession, Content, Part
from ai_model import AIModelFactory
from vertexai.language_models import ChatModel


class TestVertexAiFactoryGemini(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.factory = AIModelFactory()
        cls.model_name = "gemini-1.0-pro-002"

    def test_get_model(self):
        model = self.factory.get_model(self.model_name)
        self.assertIsInstance(model, GenerativeModel)

    def test_get_chat(self):
        chat = self.factory.get_chat(self.model_name)
        self.assertIsInstance(chat, ChatSession)

    def test_get_chat_with_history(self):
        history = [
            Content(role="user", parts=[Part.from_text("Hello")]),
            Content(role="model", parts=[Part.from_text("Hi")]),
            Content(role="user", parts=[Part.from_text("How are you?")]),
        ]
        chat = self.factory.get_chat(self.model_name, history)
        self.assertIsInstance(chat, ChatSession)

    def test_send_message(self):
        chat = self.factory.get_chat(self.model_name)
        resp = chat.send_message("Who was the first president of the United States?")
        self.assertIsInstance(chat.history, list)
        self.assertIsInstance(chat.history[0], Content)
        self.assertIsInstance(resp.text, str)


class TestVertexAiFactoryBison(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.factory = AIModelFactory()
        cls.model_name = "chat-bison@002"

    def test_get_model(self):
        model = self.factory.get_model(self.model_name)
        self.assertIsInstance(model, ChatModel)

    def test_get_chat(self):
        chat = self.factory.get_chat(self.model_name)
        self.assertIsInstance(chat, vertexai.language_models.ChatSession)

    def test_get_chat_with_history(self):
        history = [
            Content(role="user", parts=[Part.from_text("Hello")]),
            Content(role="model", parts=[Part.from_text("Hi")]),
            Content(role="user", parts=[Part.from_text("How are you?")]),
        ]
        chat = self.factory.get_chat(self.model_name, history)
        self.assertIsInstance(chat, vertexai.language_models.ChatSession)

    def test_send_message(self):
        chat = self.factory.get_chat(self.model_name)
        resp = chat.send_message("Who was the first president of the United States?")
        self.assertIsInstance(chat.message_history, list)
        self.assertIsInstance(
            chat.message_history[0], vertexai.language_models.ChatMessage
        )
        self.assertIsInstance(resp.text, str)


if __name__ == "__main__":
    unittest.main()
