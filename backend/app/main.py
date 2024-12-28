"""Main file for FastAPI server"""

from fastapi import FastAPI, HTTPException

from ampf.fastapi.static_file_response import StaticFileResponse
from app.config import ServerConfig
from app.logging_conf import setup_logging

from app.routers import auth, chats, config, files, upgrade

from app.dependencies import ServerConfigDep, lifespan
from .routers import users, agents, knowledge_base


setup_logging()

app = FastAPI(lifespan=lifespan)

if ServerConfig().profiler:
    from app.middleware_profile import ProfilerMiddleware

    app.add_middleware(ProfilerMiddleware)


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


@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    if not full_path.startswith("api/"):
        return StaticFileResponse("static/browser", full_path)
    else:
        raise HTTPException(status_code=404, detail="Not found")
