"""Main file for FastAPI server"""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from app.logging_conf import setup_logging
from app.routers import auth, chats, config, files, upgrade

from app.dependencies import ServerConfigDep
from .routers import users, agents, knowledge_base


setup_logging()

app = FastAPI()

app.include_router(prefix="/api", router=auth.router)
app.include_router(prefix="/api/config", router=config.router)
app.include_router(prefix="/api/users", router=users.router)
app.include_router(prefix="/api/files", router=files.router)

app.include_router(prefix="/api/chats", router=chats.router)
app.include_router(prefix="/api/agents", router=agents.router)
app.include_router(prefix="/api/knowledge-base", router=knowledge_base.router)
app.include_router(prefix="/api/upgrade", router=upgrade.router)

# @app.get("/api/auth")
# async def auth_google(
#     user_service: users.UserServiceDep, request: Request, response: Response
# ):
#     user_data = await session_manager.auth(request, response)
#     if user_data:
#         user = user_service.get(user_data["email"])
#         if user:
#             return JSONResponse(status_code=200, content=user_data)
#         else:
#             return JSONResponse(status_code=404, content=user_data)


@app.get("/api/user")
async def user_get(user_service: users.UserServiceDep, request: Request):
    if not request.state.session_data.api_user:
        request.state.session_data.api_user = user_service.get(
            request.state.session_data.user.email
        )
    return request.state.session_data.api_user


@app.get("/api/ping")
async def ping() -> None:
    """Just for keep container alive"""


@app.get("/api/models")
async def models_get_all(config: ServerConfigDep) -> list[str]:
    return [m.strip() for m in config.get("models").split(",")]


# fmt: off
# Angular static files - it have to be at the end of file
app.mount("/", StaticFiles(directory="static/browser", html=True, check_dir=False), name="static")
# fmt: on
