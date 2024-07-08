from gcp import Storage
from .agent_model import Agent


class AgentService:

    def create(self, user_email: str, agent: Agent):
        storage = Storage(f"user/{user_email}/agent", Agent, key_name="name")
        storage.save(agent)
