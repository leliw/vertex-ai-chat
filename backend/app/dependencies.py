"""This module contains dependencies for FastAPI endpoints."""

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Request

load_dotenv()


class InsufficientPermissionsError(HTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="Insufficient permissions.")


def get_current_user_id(request: Request) -> str:
    """Returns the current user's ID from the session."""
    return request.state.session_data.user.email


class Authorize:
    """Dependency for authorizing users based on their role."""

    def __init__(self, required_role: str):
        self.required_role = required_role

    def __call__(self, user_id: str = Depends(get_current_user_id)) -> bool:
        if user_id == "marcin.leliwa@gmail.com":
            return True
        else:
            raise InsufficientPermissionsError()
