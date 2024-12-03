"""Upgrade router. 

It shoult be called at night to upgrade the system.
All steps have to be repeatable without any side effects.
"""
from fastapi import APIRouter, Depends

from app.dependencies import Authorize
from app.routers.users import UserServiceDep


router = APIRouter(tags=["upgrade"])


@router.post("", dependencies=[Depends(Authorize("admin"))])
async def upgrade(user_service: UserServiceDep) -> None:
    # v.0.6.4
    user_service.upgrade()
