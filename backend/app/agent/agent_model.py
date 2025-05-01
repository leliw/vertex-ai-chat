from typing import List, Optional
from pydantic import BaseModel, Field


class Agent(BaseModel):
    name: str
    description: Optional[str] = None
    ai_model_name: Optional[str] = None
    system_prompt: Optional[str] = None
    keywords: Optional[List[str]] = Field(default_factory=list)
    """ Old version fields"""
    o_model_name: Optional[str] = Field(None, alias="model_name")

    def __init__(self, **data):
        """Convert old version fields to new version fields"""
        super().__init__(**data)
        self.ai_model_name = self.ai_model_name or self.o_model_name
