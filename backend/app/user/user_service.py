from typing import List, Optional

from ampf.auth import UserServiceBase
from ampf.base import AmpfBaseFactory

from .user_model import User, UserHeader, UserInDB


class UserService(UserServiceBase):
    def __init__(self, factory: AmpfBaseFactory):
        super().__init__()
        self.storage_new = factory.create_storage("users", UserInDB, key_name="email")
        self.storage_old = factory.create_storage("user", UserInDB, key_name="email")

    def get(self, email: str) -> Optional[User]:
        user_in_db = self.storage_old.get(email)
        return User(**dict(user_in_db)) if user_in_db else None

    def get_all(self) -> List[UserHeader]:
        return [
            UserHeader(**i.model_dump(by_alias=True))
            for i in self.storage_old.get_all()
        ]

    def put(self, email: str, user: User) -> None:
        user_in_db = UserInDB(**dict(user))
        self.storage_new.put(email, user_in_db)
        self.storage_old.put(email, user_in_db)

    def delete(self, email: str) -> None:
        self.storage_new.delete(email)
        self.storage_old.delete(email)

    def is_empty(self) -> bool:
        return self.storage_old.is_empty()

    def get_user_by_email(self, email: str) -> User:
        return self.get(email)
