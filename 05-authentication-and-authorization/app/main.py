from fastapi import FastAPI

from app.api.routes.auth import router as auth_router
from app.api.routes.users import router as users_router


def create_app() -> FastAPI:
    app = FastAPI(title="FastAPI Authentication", version="1.0.0")
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(users_router, prefix="/api/v1")
    return app


app = create_app()
