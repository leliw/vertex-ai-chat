from fastapi import APIRouter

from app.dependencies import AgentServiceDep, UserEmailDep

from ..agent import Agent


router = APIRouter(
    tags=["agent"],
)
AGENT_PATH = "/{agent_name}"


@router.post("", response_model=Agent)
def create(agent: Agent, user_email: UserEmailDep, service: AgentServiceDep):
    """Creates a new AI agent for current user."""
    service.create(user_email, agent)
    return agent


@router.get("", response_model=list[Agent])
def get_all(user_email: UserEmailDep, service: AgentServiceDep):
    """Returns a list of AI agents for current user."""
    return service.get_all(user_email)


@router.get(AGENT_PATH, response_model=Agent)
def get(agent_name: str, user_email: UserEmailDep, service: AgentServiceDep):
    """Returns an AI agent by name."""
    return service.get(user_email, agent_name)


@router.put(AGENT_PATH, response_model=Agent)
def put(
    agent_name: str, agent: Agent, user_email: UserEmailDep, service: AgentServiceDep
):
    """Updates an AI agent."""
    service.put(user_email, agent_name, agent)
    return agent


@router.delete(AGENT_PATH)
def delete(agent_name: str, user_email: UserEmailDep, service: AgentServiceDep):
    """Deletes an AI agent."""
    service.delete(user_email, agent_name)
