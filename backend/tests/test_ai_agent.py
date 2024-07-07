import unittest

from ai_agents import AIAgent


class TestAIAgent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.agent = AIAgent(model_name="gemini-1.5-flash")

    def test_run(self):
        response = self.agent.run("Who was the first president of the United States?")

        self.assertIn("George Washington", response)

    def test_chat(self):
        chat = self.agent.start_chat()
        response = chat.send_message(
            "Who was the first president of the United States?"
        )
        history = chat.get_history()
        self.assertIn("George Washington", response)
        chat = self.agent.start_chat(history)
        response = chat.send_message("Who was next?")
        self.assertIn("John Adams", response)

    def test_chat_streaming(self):
        chat = self.agent.start_chat(enable_automatic_function_calling=False)
        g = chat.send_message_streaming(
            "Who was the first president of the United States?"
        )
        response = ""
        for chunk in g:
            response += chunk.text
        self.assertIn("George Washington", response)
