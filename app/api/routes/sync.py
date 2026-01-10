from fastapi import APIRouter, Depends

from app.api.deps import get_store, require_auth
from app.schemas.errors import ErrorResponse
from app.schemas.sync import PushRequest, PushResponse, SyncChangesResponse
from app.services.sync import SyncService
from app.state import InMemoryStore

router = APIRouter(prefix="/sync", tags=["sync"])


def get_sync_service(store: InMemoryStore = Depends(get_store)) -> SyncService:
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
    return sync_service.get_changes(since=since)


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
    return sync_service.push_changes(payload)
