from typing import Any, Dict, Optional
from uuid import uuid4

from ampf.auth import AuthUser
from pydantic import Field, model_serializer


class UserHeader(AuthUser):
    user_id: str = Field(default_factory=lambda: str(uuid4()))
    given_name: Optional[str] = None
    family_name: Optional[str] = None


class User(UserHeader):
    terms_accepted: bool = False


class UserInDB(User):
    @model_serializer
    def ser_model(self) -> Dict[str, Any]:
        self.password = None
        return dict(self)
