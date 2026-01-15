from fastapi import APIRouter, Depends

from app.api.deps_v2 import get_mongo_store_dep, get_redis_cache_dep
from app.schemas.auth import LoginRequest, RefreshRequest, TokenResponse
from app.schemas.errors import ErrorResponse
from app.services.auth_v2 import AuthService
from app.database.mongo import MongoStore

router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_service(
    store: MongoStore = Depends(get_mongo_store_dep),
    redis=Depends(get_redis_cache_dep),
) -> AuthService:
    return AuthService(store, redis)


@router.post(
    "/login",
    response_model=TokenResponse,
    responses={401: {"model": ErrorResponse}},
)
async def login(
    payload: LoginRequest, auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.login(payload)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    responses={401: {"model": ErrorResponse}},
)
async def refresh_tokens(
    payload: RefreshRequest, auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.refresh_tokens(payload)
