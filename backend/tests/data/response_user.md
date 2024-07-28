## app/user/user_model.py

```python
from pydantic import BaseModel


class User(BaseModel):
    email: str
    name: str
    password_hash: str

```

## app/user/user_service.py

```python
"""Service for managing users."""

from typing import List

from .user_model import User


class UserService:
    """Service for managing users."""

    def __init__(self, storage):
        self.storage = storage

    def create(self, user: User):
        """Create a new user."""
        self.storage.save(user.email, user)

    def get(self, email: str) -> User:
        """Get a user by email."""
        return self.storage.get(email)

    def get_all(self) -> List[User]:
        """Get all users."""
        return [self.storage.get(email) for email in self.storage.keys()]

    def update(self, email: str, user: User):
        """Update a user."""
        self.storage.put(email, user)

    def delete(self, email: str):
        """Delete a user."""
        self.storage.delete(email)

```

## app/user/user_router.py

```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from .user_model import User
from .user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])

# Inject the user service
user_service = UserService(storage=None)  # Replace with actual storage implementation


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(user: User):
    """Create a new user."""
    try:
        user_service.create(user)
        return JSONResponse(
            content={"message": "User created successfully"},
            status_code=status.HTTP_201_CREATED,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error creating user: {e}"
        )


@router.get("/{email}")
async def get_user(email: str):
    """Get a user by email."""
    try:
        user = user_service.get(email)
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found: {e}"
        )


@router.get("/")
async def get_all_users():
    """Get all users."""
    try:
        users = user_service.get_all()
        return users
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting users: {e}",
        )


@router.put("/{email}")
async def update_user(email: str, user: User):
    """Update a user."""
    try:
        user_service.update(email, user)
        return JSONResponse(
            content={"message": "User updated successfully"},
            status_code=status.HTTP_200_OK,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error updating user: {e}"
        )


@router.delete("/{email}")
async def delete_user(email: str):
    """Delete a user."""
    try:
        user_service.delete(email)
        return JSONResponse(
            content={"message": "User deleted successfully"},
            status_code=status.HTTP_200_OK,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error deleting user: {e}"
        )

```