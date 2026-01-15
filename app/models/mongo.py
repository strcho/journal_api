from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class MongoEntry(BaseModel):
    id: str
    payload_encrypted: str
    payload_version: int
    attachment_ids: list[str]
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    revision: Optional[int] = None


class MongoAttachmentMeta(BaseModel):
    id: str
    sha256: str
    size_bytes: int
    mime_type: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    revision: Optional[int] = None


class MongoAttachmentContent(BaseModel):
    id: str
    content: bytes


class MongoRefreshToken(BaseModel):
    token: str
    device_id: str
    user_email: str
    created_at: datetime


class MongoSequence(BaseModel):
    name: str = "_id"
    value: int
