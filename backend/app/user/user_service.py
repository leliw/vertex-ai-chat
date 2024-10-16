from typing import List, Optional

from ampf.base import AmpfBaseFactory

from .user_model import User, UserHeader


class UserService:
    def __init__(self, factory: AmpfBaseFactory):
        self.storage = factory.create_storage("user", User, key_name="email")

    def create(self, user: User) -> User:
        key = self.storage.get_key(user)
        if self.storage.get(key):
            raise ValueError("User already exists")
        self.storage.save(user)
        return user

    def get(self, email: str) -> Optional[User]:
        return self.storage.get(email)

    def get_all(self) -> List[UserHeader]:
        return [
            UserHeader(**i.model_dump(by_alias=True)) for i in self.storage.get_all()
        ]

    def update(self, email: str, user: User) -> Optional[User]:
        self.storage.put(email, user)
        return user

    def delete(self, email: str) -> bool:
        return self.storage.delete(email)
