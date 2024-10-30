from typing import List, Optional

from ampf.auth import UserServiceBase
from ampf.base import AmpfBaseFactory

from .user_model import User, UserHeader


class UserService(UserServiceBase):
    def __init__(self, factory: AmpfBaseFactory):
        self.storage = factory.create_storage("user", User, key_name="email")

    def get(self, email: str) -> Optional[User]:
        return self.storage.get(email)

    def get_all(self) -> List[UserHeader]:
        return [
            UserHeader(**i.model_dump(by_alias=True)) for i in self.storage.get_all()
        ]

    def put(self, email: str, user: User) -> Optional[User]:
        self.storage.put(email, user)
        return user
    
    def delete(self, email: str) -> bool:
        return self.storage.delete(email)
    
    def is_empty(self) -> bool:
        return self.storage.is_empty()
    
    def get_user_by_email(self, email: str) -> User:
        return self.get(email)
