from fastapi import FastAPI

from app.api.routes.orders import router
from app.core.errors import install_error_handlers


def create_app() -> FastAPI:
    app = FastAPI(title="FastAPI Validation Guide", version="1.0.0")
    install_error_handlers(app)
    app.include_router(router, prefix="/api/v1")
    return app


app = create_app()
