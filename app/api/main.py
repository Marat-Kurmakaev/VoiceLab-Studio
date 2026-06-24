from __future__ import annotations

import uvicorn
from fastapi import FastAPI

from app.api.routers.models import router as models_router
from app.api.routers.tasks import router as tasks_router
from app.core.config import Settings, get_settings
from app.core.logging import configure_logging


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(title=settings.app_name)
    app.include_router(models_router)
    app.include_router(tasks_router)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "environment": settings.app_env}

    return app


app = create_app()


def run() -> None:
    settings = get_settings()
    uvicorn.run("app.api.main:app", host=settings.api_host, port=settings.api_port)
