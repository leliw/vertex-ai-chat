import unittest

from chat_service import ChatHistoryException, ChatMessage, ChatService


class TestChatService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.service = ChatService()

    def test_get_answer(self):
        history = []
        message = ChatMessage(author="user", content="Hello")

        answer, chat_history = self.service.get_answer(history, message)

        self.assertEqual(answer.author, "ai")
        self.assertIsInstance(answer.content, str)
        self.assertEqual(chat_history[0], message)
        self.assertEqual(chat_history[1], answer)

    def test_get_answer_async(self):
        history = []
        message = ChatMessage(author="user", content="Hello")

        text = ""
        try:
            for p in self.service.get_answer_async(history, message):
                text += p
        except ChatHistoryException as e:
            chat_history = e.history
        answer = ChatMessage(author="ai", content=text)
        self.assertEqual(answer.author, "ai")
        self.assertIsInstance(answer.content, str)
        self.assertEqual(chat_history[0], message)
        self.assertEqual(chat_history[1], answer)


if __name__ == "__main__":
    unittest.main()
