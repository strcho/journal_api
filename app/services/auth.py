import uuid

from fastapi import status

from app.core.errors import http_error
from app.schemas.auth import LoginRequest, RefreshRequest, TokenResponse
from app.state import InMemoryStore


class AuthService:
    def __init__(self, store: InMemoryStore):
        self.store = store

    def login(self, payload: LoginRequest) -> TokenResponse:
        device_id = str(uuid.uuid4())
        access_token = str(uuid.uuid4())
        refresh_token = str(uuid.uuid4())

        self.store.active_access_tokens.add(access_token)
        self.store.refresh_token_index[refresh_token] = device_id

        return TokenResponse(
            accessToken=access_token,
            refreshToken=refresh_token,
            deviceId=device_id,
        )

    def refresh_tokens(self, payload: RefreshRequest) -> TokenResponse:
        if payload.refreshToken not in self.store.refresh_token_index:
            raise http_error(
                code="AUTH_TOKEN_INVALID",
                message="Refresh token is invalid.",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        device_id = self.store.refresh_token_index[payload.refreshToken]
        if device_id != payload.deviceId:
            raise http_error(
                code="AUTH_FORBIDDEN",
                message="Refresh token does not belong to the device.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        access_token = str(uuid.uuid4())
        refresh_token = str(uuid.uuid4())
        self.store.active_access_tokens.add(access_token)
        self.store.refresh_token_index[refresh_token] = device_id

        return TokenResponse(
            accessToken=access_token,
            refreshToken=refresh_token,
            deviceId=device_id,
        )
