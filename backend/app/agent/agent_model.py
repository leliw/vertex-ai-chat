from typing import List, Optional
from pydantic import BaseModel, Field


class Agent(BaseModel):
    name: str
    description: Optional[str] = None
    model_name: str
    system_prompt: Optional[str] = None
    keywords: Optional[List[str]] = Field(default_factory=list)
