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
