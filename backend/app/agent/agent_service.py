from gcp import Storage
from .agent_model import Agent


class AgentService:
    def _crete_storage(self, user_email: str):
        return Storage(f"user/{user_email}/agent", Agent, key_name="name")

    def create(self, user_email: str, agent: Agent):
        storage = self._crete_storage(user_email)
        storage.save(agent)

    def get_all(self, user_email: str):
        storage = self._crete_storage(user_email)
        return storage.keys()

    def get(self, user_email: str, agent_name: str):
        storage = self._crete_storage(user_email)
        return storage.get(agent_name)

    def put(self, user_email: str, agent_name: str, agent: Agent):
        storage = self._crete_storage(user_email)
        storage.put(agent_name, agent)

    def delete(self, user_email: str, agent_name: str):
        storage = self._crete_storage(user_email)
        storage.delete(agent_name)
