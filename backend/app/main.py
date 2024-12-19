"""Main file for FastAPI server"""

from fastapi import FastAPI
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
