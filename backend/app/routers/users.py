from fastapi import APIRouter, Depends, Request

from app.dependencies import Authorize

from ..user import User, UserService

service = UserService()
router = APIRouter(tags=["users"])


@router.post("/register")
async def register(request: Request, user: User):
    service.create(user)
    request.state.session_data.api_user = user
    return user


@router.get("/users", dependencies=[Depends(Authorize("admin"))])
async def get_all():
    return service.get_all()


@router.get("/users/{email}", dependencies=[Depends(Authorize("admin"))])
async def get_by_email(email: str):
    return service.get(email)


@router.put("/users/{email}", dependencies=[Depends(Authorize("admin"))])
async def update(email: str, user: User):
    return service.update(email, user)


@router.delete("/users/{email}", dependencies=[Depends(Authorize("admin"))])
async def delete(email: str):
    return service.delete(email)

