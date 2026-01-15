import uuid
from datetime import datetime
from typing import Optional

from fastapi import status

from app.core.errors import http_error
from app.database.mongo import MongoStore
from app.database.redis import RedisCache
from app.schemas.auth import LoginRequest, RefreshRequest, TokenResponse
from app.models.mongo import MongoRefreshToken


class AuthService:
    def __init__(self, store: MongoStore, redis: RedisCache):
        self.store = store
        self.redis = redis

    async def login(self, payload: LoginRequest) -> TokenResponse:
        device_id = str(uuid.uuid4())
        access_token = str(uuid.uuid4())
        refresh_token = str(uuid.uuid4())

        mongo_token = MongoRefreshToken(
            token=refresh_token,
            device_id=device_id,
            user_email=payload.email,
            created_at=datetime.utcnow(),
        )
        await self.store.create_refresh_token(mongo_token)

        await self.redis.set(f"access_token:{access_token}", "1", expire=3600)

        return TokenResponse(
            accessToken=access_token,
            refreshToken=refresh_token,
            deviceId=device_id,
        )

    async def refresh_tokens(self, payload: RefreshRequest) -> TokenResponse:
        token_doc = await self.store.get_refresh_token(payload.refreshToken)
        if not token_doc:
            raise http_error(
                code="AUTH_TOKEN_INVALID",
                message="Refresh token is invalid.",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        if token_doc["device_id"] != payload.deviceId:
            raise http_error(
                code="AUTH_FORBIDDEN",
                message="Refresh token does not belong to device.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        device_id = token_doc["device_id"]
        user_email = token_doc["user_email"]

        await self.store.delete_refresh_token(payload.refreshToken)

        access_token = str(uuid.uuid4())
        refresh_token = str(uuid.uuid4())

        mongo_token = MongoRefreshToken(
            token=refresh_token,
            device_id=device_id,
            user_email=user_email,
            created_at=datetime.utcnow(),
        )
        await self.store.create_refresh_token(mongo_token)

        await self.redis.set(f"access_token:{access_token}", "1", expire=3600)

        return TokenResponse(
            accessToken=access_token,
            refreshToken=refresh_token,
            deviceId=device_id,
        )

    async def validate_access_token(self, token: str) -> bool:
        return await self.redis.exists(f"access_token:{token}")
