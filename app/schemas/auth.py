from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    accessToken: str
    refreshToken: str
    deviceId: str


class RefreshRequest(BaseModel):
    refreshToken: str
    deviceId: str
