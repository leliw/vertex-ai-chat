from fastapi import APIRouter, Depends, Request

from app.dependencies import Authorize
from app.user import User, UserService


class UserRouter:
    def __init__(self, service: UserService):
        self.service = service
        self.router = APIRouter(tags=["user"])
        self.router.post("/register")(self.register)
        self.router.get("/users", dependencies=[Depends(Authorize("admin"))])(
            self.get_all
        )

    async def register(self, request: Request, user: User):
        self.service.create(user)
        request.state.session_data.api_user = user
        return user

    async def get_all(self):
        return self.service.get_all()
