from typing import Optional

from fastapi import Depends, Header, Request, status

from app.core.errors import http_error
from app.state_v2 import get_mongo_store, get_redis_cache
from app.database.mongo import MongoStore


async def get_mongo_store_dep() -> MongoStore:
    return await get_mongo_store()


async def get_redis_cache_dep():
    return await get_redis_cache()


async def require_auth(
    authorization: Optional[str] = Header(None, convert_underscores=False),
    redis_cache=Depends(get_redis_cache_dep),
) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise http_error(
            code="AUTH_TOKEN_INVALID",
            message="Missing or invalid Authorization header.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    token = authorization.replace("Bearer ", "", 1).strip()

    is_valid = await redis_cache.get(f"access_token:{token}")
    if is_valid != "1":
        raise http_error(
            code="AUTH_TOKEN_INVALID",
            message="Access token is invalid or expired.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    return token
