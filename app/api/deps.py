from typing import Optional

from fastapi import Depends, Header, Request, status

from app.core.errors import http_error
from app.state import InMemoryStore


def get_store(request: Request) -> InMemoryStore:
    return request.app.state.store


def require_auth(
    authorization: Optional[str] = Header(None, convert_underscores=False),
    store: InMemoryStore = Depends(get_store),
) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise http_error(
            code="AUTH_TOKEN_INVALID",
            message="Missing or invalid Authorization header.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    token = authorization.replace("Bearer ", "", 1).strip()
    if token not in store.active_access_tokens:
        raise http_error(
            code="AUTH_TOKEN_INVALID",
            message="Access token is invalid or expired.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    return token
