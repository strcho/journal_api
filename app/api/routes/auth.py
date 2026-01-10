from fastapi import APIRouter, Depends

from app.api.deps import get_store
from app.schemas.auth import LoginRequest, RefreshRequest, TokenResponse
from app.schemas.errors import ErrorResponse
from app.services.auth import AuthService
from app.state import InMemoryStore

router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_service(store: InMemoryStore = Depends(get_store)) -> AuthService:
    return AuthService(store)


@router.post("/login", response_model=TokenResponse, responses={401: {"model": ErrorResponse}})
async def login(payload: LoginRequest, auth_service: AuthService = Depends(get_auth_service)):
    return auth_service.login(payload)


@router.post("/refresh", response_model=TokenResponse, responses={401: {"model": ErrorResponse}})
async def refresh_tokens(
    payload: RefreshRequest, auth_service: AuthService = Depends(get_auth_service)
):
    return auth_service.refresh_tokens(payload)
