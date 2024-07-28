from pydantic import BaseModel


class Agent(BaseModel):
    name: str
    description: str
    model_name: str
    system_prompt: str
