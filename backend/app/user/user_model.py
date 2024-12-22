from typing import Any, Dict, Optional
from uuid import uuid4
from pydantic import Field, model_serializer

from ampf.auth import AuthUser


class UserHeader(AuthUser):
    user_id: str = Field(default_factory=lambda: str(uuid4()))
    given_name: Optional[str] = None
    family_name: Optional[str] = None


class User(UserHeader):
    terms_accepted: bool = False

    """ Old version fields"""
    o_first__name: Optional[str] = Field(None, alias="firstName")
    o_last_name: Optional[str] = Field(None, alias="lastName")
    o_terms_accepted: bool = Field(False, alias="termsAccepted")
    o_picture_url: Optional[str] = Field(None, alias="pictureUrl")

    def __init__(self, **data):
        """Convert old version fields to new version fields"""
        super().__init__(**data)
        self.given_name = self.given_name or self.o_first__name
        self.o_first__name = None
        self.family_name = self.family_name or self.o_last_name
        self.o_last_name = None
        self.terms_accepted = self.terms_accepted or self.o_terms_accepted
        self.o_terms_accepted = None
        self.picture = self.picture or self.o_picture_url
        self.o_picture_url = None


class UserInDB(User):
    @model_serializer
    def ser_model(self) -> Dict[str, Any]:
        self.password = None
        return dict(self)
