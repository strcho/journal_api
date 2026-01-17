from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field
from app.schemas.journal import JournalChange


class EntryChange(BaseModel):
    id: str = Field(..., description="UUID")
    journalId: str = Field(..., description="Journal UUID")
    payloadEncrypted: str
    payloadVersion: int
    attachmentIds: List[str] = []
    createdAt: datetime
    updatedAt: datetime
    deletedAt: Optional[datetime] = None
    revision: Optional[int] = Field(
        None, description="Client-side revision; server overwrites on accept."
    )


class AttachmentMeta(BaseModel):
    id: str = Field(..., description="Attachment UUID")
    sha256: str
    sizeBytes: int
    mimeType: str
    createdAt: datetime
    updatedAt: datetime
    deletedAt: Optional[datetime] = None
    revision: Optional[int] = None


class SyncChangesResponse(BaseModel):
    latestRevision: int
    entries: List[EntryChange]
    attachments: List[AttachmentMeta]
    journals: List[JournalChange] = []


class PushRequest(BaseModel):
    entries: List[EntryChange] = []
    attachmentsMeta: List[AttachmentMeta] = []
    journals: List[JournalChange] = []


class PushResponse(BaseModel):
    accepted: List[str]
    conflicts: List[str]
    missingAttachments: List[str]
