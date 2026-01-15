import os
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api.routes import health
from app.api.routes.auth_v2 import router as auth_router
from app.api.routes.sync_v2 import router as sync_router
from app.api.routes.attachments_v2 import router as attachments_router
from app.api.routes.storage_v2 import router as storage_router
from app.state_v2 import init_databases, close_databases


@asynccontextmanager
async def lifespan(app: FastAPI):
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    db_name = os.getenv("MONGODB_DB_NAME", "journal_db")
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

    await init_databases(mongodb_url, db_name, redis_url)

    yield

    await close_databases()


def create_app() -> FastAPI:
    app = FastAPI(title="Journal API", lifespan=lifespan)

    app.include_router(health.router)
    app.include_router(auth_router)
    app.include_router(sync_router)
    app.include_router(attachments_router)
    app.include_router(storage_router)

    return app


app = create_app()
