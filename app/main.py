from fastapi import FastAPI

from app.api.routes import attachments, auth, health, sync
from app.state import InMemoryStore


def create_app() -> FastAPI:
    app = FastAPI(title="Journal API")
    app.state.store = InMemoryStore()

    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(sync.router)
    app.include_router(attachments.router)

    return app


app = create_app()
