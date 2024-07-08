from fastapi import APIRouter, Request

from ..agent import Agent, AgentService


service = AgentService()
router = APIRouter(
    tags=["agent"],
)
AGENT_PATH = "/{agemt_name}"


@router.post("", response_model=Agent)
def create(request: Request, agent: Agent):
    """Creates a new AI agent for current user."""
    user_email = request.state.session_data.user.email
    service.create(user_email, agent)
    return agent


@router.get("", response_model=list[str])
def get_all(request: Request):
    """Returns a list of AI agents for current user."""
    user_email = request.state.session_data.user.email
    return service.get_all(user_email)


@router.get(AGENT_PATH, response_model=Agent)
def get(request: Request, agent_name: str):
    """Returns an AI agent by name."""
    user_email = request.state.session_data.user.email
    agent = service.get(user_email, agent_name)
    return agent


@router.put(AGENT_PATH, response_model=Agent)
def put(request: Request, agent_name: str, agent: Agent):
    """Updates an AI agent."""
    user_email = request.state.session_data.user.email
    service.put(user_email, agent_name, agent)
    return agent


@router.delete(AGENT_PATH)
def delete(request: Request, agent_name: str):
    """Deletes an AI agent."""
    user_email = request.state.session_data.user.email
    service.delete(user_email, agent_name)
