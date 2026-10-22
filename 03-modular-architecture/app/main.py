from fastapi import FastAPI

from app.api.routes.products import router


def create_app() -> FastAPI:
    app = FastAPI(title="FastAPI Modular Architecture", version="1.0.0")
    app.include_router(router, prefix="/api/v1")
    return app


app = create_app()
