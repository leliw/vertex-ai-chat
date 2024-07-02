from gcp import Storage
from .user_model import User


class UserStorage(Storage):
    def __init__(self):
        super().__init__("user", User, key_name="email")
