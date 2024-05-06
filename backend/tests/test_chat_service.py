import unittest

from chat_service import ChatMessage, ChatService


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
        for p in self.service.get_answer_async(history, message):
            if isinstance(p, str):
                text += p
            else:
                chat_history = p
        answer = ChatMessage(author="ai", content=text)
        self.assertEqual(answer.author, "ai")
        self.assertIsInstance(answer.content, str)
        self.assertEqual(chat_history[0], message)
        self.assertEqual(chat_history[1], answer)


if __name__ == "__main__":
    unittest.main()
