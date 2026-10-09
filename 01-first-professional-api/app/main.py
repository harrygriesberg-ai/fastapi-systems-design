from fastapi import FastAPI

from app.api.routes.users import router as users_router
from app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version="1.0.0")

    @app.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {"status": "ok", "environment": settings.app_env}

    app.include_router(users_router, prefix="/api/v1")
    return app


app = create_app()
