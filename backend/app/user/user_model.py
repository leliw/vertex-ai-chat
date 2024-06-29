from typing import Optional
from uuid import uuid4
from pydantic import BaseModel, Field


class UserHeader(BaseModel):
    user_id: str = Field(default_factory=lambda: str(uuid4()))
    email: str
    name: str
    first__name: Optional[str] = Field(None, alias="firstName")
    last_name: Optional[str] = Field(None, alias="lastName")


class User(UserHeader):
    picture_url: Optional[str] = Field(None, alias="pictureUrl")
