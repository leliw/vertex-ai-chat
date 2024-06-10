import datetime
import unittest

from gcp import FileStorage
from app.chat.chat_service import (
    ChatHistoryException,
    ChatMessage,
    ChatService,
    ChatSession,
)

model_name = "gemini-1.0-pro-002"


class TestChatService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        file_storage = FileStorage("vertex-ai-chat-dev-session-files")
        cls.service = ChatService(file_storage)

    def test_get_answer(self):
        history = []
        message = ChatMessage(author="user", content="Hello")

        answer, chat_history = self.service.get_answer(model_name, history, message)

        self.assertEqual(answer.author, "ai")
        self.assertIsInstance(answer.content, str)
        self.assertEqual(chat_history[0], message)
        self.assertEqual(chat_history[1], answer)

    def test_get_answer_async(self):
        session = ChatSession(
            chat_session_id="x",
            user="x",
            created=datetime.datetime.now(),
            history=[],
        )
        message = ChatMessage(author="user", content="Hello")
        text = ""
        try:
            for p in self.service.get_answer_async(model_name, session, message, []):
                text += p.value
        except ChatHistoryException as e:
            chat_history = e.chat_session.history
        answer = ChatMessage(author="ai", content=text)
        self.assertEqual(answer.author, "ai")
        self.assertIsInstance(answer.content, str)
        self.assertEqual(chat_history[0], message)
        self.assertEqual(chat_history[1], answer)


if __name__ == "__main__":
    unittest.main()
