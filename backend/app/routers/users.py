from typing import Annotated
from fastapi import APIRouter, Depends, Request

from app.dependencies import Authorize, FactoryDep

from ..user import UserHeader, User, UserService


router = APIRouter(tags=["users"])


def get_user_service(factory: FactoryDep):
    return UserService(factory)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


@router.post("/register")
async def register(service: UserServiceDep, request: Request, user: User):
    service.create(user)
    request.state.session_data.api_user = user
    return user


@router.get("/users", dependencies=[Depends(Authorize("admin"))])
async def get_all(service: UserServiceDep) -> list[UserHeader]:
    return service.get_all()


@router.get("/users/{email}", dependencies=[Depends(Authorize("admin"))])
async def get_by_email(service: UserServiceDep, email: str):
    return service.get(email)


@router.put("/users/{email}", dependencies=[Depends(Authorize("admin"))])
async def update(service: UserServiceDep, email: str, user: User):
    return service.update(email, user)


@router.delete("/users/{email}", dependencies=[Depends(Authorize("admin"))])
async def delete(service: UserServiceDep, email: str):
    return service.delete(email)
