import logging
from typing import List

from ampf.auth import UserServiceBase
from ampf.base import BaseFactory, KeyNotExistsException

from .user_model import User, UserHeader, UserInDB


class UserService(UserServiceBase):
    def __init__(self, factory: BaseFactory):
        super().__init__()
        self.storage_new = factory.create_storage("users", UserInDB, key_name="email")
        self.storage_old = factory.create_storage("user", UserInDB, key_name="email")
        self._log = logging.getLogger(__name__)

    def initialize_storage_with_user(self, default_user: User):
        if self.is_empty():
            self._log.warning("Initializing storage with default user")
            self.create(User(**default_user.model_dump()))

    def get(self, email: str) -> User:
        user_in_db = self.storage_new.get(email)
        return User(**dict(user_in_db)) if user_in_db else None

    def get_all(self) -> List[UserHeader]:
        return [
            UserHeader(**i.model_dump(by_alias=True))
            for i in self.storage_new.get_all()
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

    def upgrade(self) -> None:
        """Upgrade the storage to the new version."""
        # For each user in the old storage,
        for o in self.storage_old.get_all():
            # if the user is not in the new storage,
            try:
                self.storage_new.get(o.email)
            except KeyNotExistsException:
                self._log.info(f"Upgrading user {o.email}")
                # put it in the new storage.
                self.storage_new.put(o.email, o)
