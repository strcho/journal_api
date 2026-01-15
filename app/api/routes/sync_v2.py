from fastapi import APIRouter, Depends

from app.api.deps_v2 import require_auth, get_mongo_store_dep
from app.schemas.errors import ErrorResponse
from app.schemas.sync import PushRequest, PushResponse, SyncChangesResponse
from app.services.sync_v2 import SyncService
from app.database.mongo import MongoStore

router = APIRouter(prefix="/sync", tags=["sync"])


def get_sync_service(
    store: MongoStore = Depends(get_mongo_store_dep),
) -> SyncService:
    return SyncService(store)


@router.get(
    "/changes",
    response_model=SyncChangesResponse,
    responses={401: {"model": ErrorResponse}},
)
async def get_changes(
    since: int = 0,
    token: str = Depends(require_auth),
    sync_service: SyncService = Depends(get_sync_service),
):
    del token
    return await sync_service.get_changes(since=since)


@router.post(
    "/push",
    response_model=PushResponse,
    responses={401: {"model": ErrorResponse}},
)
async def push_changes(
    payload: PushRequest,
    token: str = Depends(require_auth),
    sync_service: SyncService = Depends(get_sync_service),
):
    del token
    return await sync_service.push_changes(payload)
