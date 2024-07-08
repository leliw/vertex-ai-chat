from fastapi import APIRouter, Request

from ..agent import Agent, AgentService


service = AgentService()
router = APIRouter(
    tags=["agent"],
)


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
