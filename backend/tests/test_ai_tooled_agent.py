import unittest

from dotenv import load_dotenv


from ai_agents.ai_tooled_agent import AITooledAgent


def get_remaining_vacation_days(year: int = None):
    """Zwraca ilość dni urlopu, które pozostały do wykorzystania w roku kalendarzowym.

    Args:
        year: Rok

    Returns:
        Ilość dni urlopu.
    """
    return 26


class TestAITooledAgent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        load_dotenv()

    def test_run_without_tools(self):
        agent = AITooledAgent(model_name="gemini-1.5-flash")

        response = agent.run("Who was the first president of the United States?")

        self.assertIn("George Washington", response)

    def test_run_with_tool_without_parameters(self):
        agent = AITooledAgent(
            model_name="gemini-1.5-flash", tools=[get_remaining_vacation_days]
        )

        response = agent.run("Ile zostało mi dni urlopu?")

        self.assertIn("26", response)

    def test_chat_with_tool(self):
        agent = AITooledAgent(
            model_name="gemini-1.5-flash", tools=[get_remaining_vacation_days]
        )
        chat = agent.start_chat()
        response = chat.send_message("Ile zostało mi dni urlopu?")

        self.assertIn("26", response)


class TestAITooledAgentWithPreparedFunction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        load_dotenv()

    def test_chat_with_prepared_tool(self):
        def base_func(email: str, year: int) -> int:
            data = {
                "jasio.fasola@wp.pl": {2023: 5, 2024: 26},
                "jan.nowak@wp.pl": {2023: 0, 2024: 12},
            }
            return data.get(email, {}).get(year, 0)

        user = "jan.nowak@wp.pl"

        def prep_func(year: int) -> int:
            """Zwraca ilość dni urlopu pozostałą do wykorzystania w danym roku kalendarzowym.

            Args:
                year: Rok
            Returns:
                Ilość dni urlopu.
            """
            return base_func(user, year)

        agent = AITooledAgent(model_name="gemini-1.5-flash", tools=[prep_func])
        chat = agent.start_chat()
        response = chat.send_message("Ile zostało mi dni urlopu z 2024 roku?")

        self.assertIn("12", response)
