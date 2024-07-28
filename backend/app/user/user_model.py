from typing import List, Optional
from uuid import uuid4
from pydantic import BaseModel, Field


class UserHeader(BaseModel):
    user_id: str = Field(default_factory=lambda: str(uuid4()))
    email: str
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    roles: Optional[List[str]] = None


class User(UserHeader):
    terms_accepted: bool = False
    picture: Optional[str] = None

    """ Old version fields"""
    name: Optional[str] = None
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
