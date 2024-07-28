"""Service for managing AI agent definitions."""

from gcp import Storage
from .agent_model import Agent


class AgentService:
    """Service for managing AI agent definitions."""

    def __init__(self, config: dict):
        self.config = config

    def _crete_storage(self, user_email: str):
        """Create storage for agents of a given user."""
        return Storage(f"users/{user_email}/agents", Agent, key_name="name")

    def create_default(self, user_email: str, model_name: str):
        """Create a default agent for a given model."""
        agent = Agent(
            name=model_name,
            description=f"Default agent for {model_name}",
            model_name=model_name,
            system_prompt="",
        )
        self.create(user_email, agent)
        return agent

    def create(self, user_email: str, agent: Agent):
        """Create a new agent for a given user."""
        storage = self._crete_storage(user_email)
        storage.save(agent)

    def get_all(self, user_email: str):
        """Return a list of agent names for a given user."""
        storage = self._crete_storage(user_email)
        keys = list(storage.keys())
        if not keys:
            model_name = self.config.get("default_model")
            self.create_default(user_email, model_name=model_name)
            keys = [model_name]
        return keys

    def get(self, user_email: str, agent_name: str):
        """Return an agent by name."""
        storage = self._crete_storage(user_email)
        return storage.get(agent_name)

    def put(self, user_email: str, agent_name: str, agent: Agent):
        """Update an agent."""
        storage = self._crete_storage(user_email)
        storage.put(agent_name, agent)

    def delete(self, user_email: str, agent_name: str):
        """Delete an agent."""
        storage = self._crete_storage(user_email)
        storage.delete(agent_name)
