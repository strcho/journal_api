from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Journal(BaseModel):
    id: str
    name: str
    color: Optional[str] = None
    createdAt: str
    updatedAt: str
    deletedAt: Optional[str] = None
    revision: Optional[int] = None


class JournalChange(BaseModel):
    id: str
    name: str
    color: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime
    deletedAt: Optional[datetime] = None
    revision: Optional[int] = None


class CreateJournalRequest(BaseModel):
    name: str
    color: Optional[str] = None


class UpdateJournalRequest(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None


class JournalListResponse(BaseModel):
    journals: list[Journal]
