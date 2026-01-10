import uuid
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

app = FastAPI()

# In-memory stores for demo purposes only.
entries_store: Dict[str, Dict] = {}
attachments_meta_store: Dict[str, Dict] = {}
attachments_content_store: Dict[str, bytes] = {}
active_access_tokens: set[str] = set()
refresh_token_index: Dict[str, str] = {}
latest_revision: int = 0


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail


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


class EntryChange(BaseModel):
    id: str = Field(..., description="UUID")
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


class PushRequest(BaseModel):
    entries: List[EntryChange] = []
    attachmentsMeta: List[AttachmentMeta] = []


class PushResponse(BaseModel):
    accepted: List[str]
    conflicts: List[str]
    missingAttachments: List[str]


def error(code: str, message: str, status_code: int) -> HTTPException:
    return HTTPException(
        status_code=status_code,
        detail=ErrorResponse(error=ErrorDetail(code=code, message=message)).dict(),
    )


def next_revision() -> int:
    global latest_revision
    latest_revision += 1
    return latest_revision


def require_auth(
    authorization: Optional[str] = Header(None, convert_underscores=False),
) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise error(
            code="AUTH_TOKEN_INVALID",
            message="Missing or invalid Authorization header.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    token = authorization.replace("Bearer ", "", 1).strip()
    if token not in active_access_tokens:
        raise error(
            code="AUTH_TOKEN_INVALID",
            message="Access token is invalid or expired.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    return token


@app.get("/")
async def root():
    return {"message": "Journal API is running"}


@app.post("/auth/login", response_model=TokenResponse, responses={401: {"model": ErrorResponse}})
async def login(payload: LoginRequest):
    # Demo: accept any credentials and issue tokens.
    device_id = str(uuid.uuid4())
    access_token = str(uuid.uuid4())
    refresh_token = str(uuid.uuid4())

    active_access_tokens.add(access_token)
    refresh_token_index[refresh_token] = device_id

    return TokenResponse(
        accessToken=access_token,
        refreshToken=refresh_token,
        deviceId=device_id,
    )


@app.post("/auth/refresh", response_model=TokenResponse, responses={401: {"model": ErrorResponse}})
async def refresh_tokens(payload: RefreshRequest):
    if payload.refreshToken not in refresh_token_index:
        raise error(
            code="AUTH_TOKEN_INVALID",
            message="Refresh token is invalid.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    device_id = refresh_token_index[payload.refreshToken]
    if device_id != payload.deviceId:
        raise error(
            code="AUTH_FORBIDDEN",
            message="Refresh token does not belong to the device.",
            status_code=status.HTTP_403_FORBIDDEN,
        )

    new_access = str(uuid.uuid4())
    new_refresh = str(uuid.uuid4())
    active_access_tokens.add(new_access)
    refresh_token_index[new_refresh] = device_id

    return TokenResponse(
        accessToken=new_access,
        refreshToken=new_refresh,
        deviceId=device_id,
    )


@app.get(
    "/sync/changes",
    response_model=SyncChangesResponse,
    responses={401: {"model": ErrorResponse}},
)
async def get_changes(since: int = 0, token: str = Depends(require_auth)):
    del token  # Not used further; dependency enforces auth.
    entry_changes = [
        EntryChange(**entry) for entry in entries_store.values() if entry["revision"] > since
    ]
    attachment_changes = [
        AttachmentMeta(**meta)
        for meta in attachments_meta_store.values()
        if meta["revision"] > since
    ]

    entry_changes.sort(key=lambda e: e.revision or 0)
    attachment_changes.sort(key=lambda a: a.revision or 0)

    return SyncChangesResponse(
        latestRevision=latest_revision,
        entries=entry_changes,
        attachments=attachment_changes,
    )


@app.post(
    "/sync/push",
    response_model=PushResponse,
    responses={401: {"model": ErrorResponse}},
)
async def push_changes(payload: PushRequest, token: str = Depends(require_auth)):
    del token
    accepted: List[str] = []
    conflicts: List[str] = []
    missing_attachments: set[str] = set()

    for entry in payload.entries:
        existing = entries_store.get(entry.id)
        if existing and entry.revision is not None and entry.revision < existing["revision"]:
            conflicts.append(entry.id)
            continue

        current_revision = next_revision()
        entry_data = entry.dict()
        entry_data["revision"] = current_revision
        entries_store[entry.id] = entry_data
        accepted.append(entry.id)

        for att_id in entry.attachmentIds:
            if att_id not in attachments_content_store:
                missing_attachments.add(att_id)

    for meta in payload.attachmentsMeta:
        existing_meta = attachments_meta_store.get(meta.id)
        if existing_meta and meta.revision is not None and meta.revision < existing_meta["revision"]:
            conflicts.append(meta.id)
            continue

        current_revision = next_revision()
        meta_data = meta.dict()
        meta_data["revision"] = current_revision
        attachments_meta_store[meta.id] = meta_data
        accepted.append(meta.id)

    return PushResponse(
        accepted=accepted,
        conflicts=conflicts,
        missingAttachments=sorted(missing_attachments),
    )


@app.put(
    "/attachments/{attachment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={401: {"model": ErrorResponse}},
)
async def upload_attachment(
    attachment_id: str, request: Request, token: str = Depends(require_auth)
):
    del token
    body = await request.body()
    attachments_content_store[attachment_id] = body
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get(
    "/attachments/{attachment_id}",
    responses={
        200: {"content": {"application/octet-stream": {}}},
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
async def download_attachment(attachment_id: str, token: str = Depends(require_auth)):
    del token
    if attachment_id not in attachments_content_store:
        raise error(
            code="RESOURCE_NOT_FOUND",
            message="Attachment not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return StreamingResponse(
        content=iter([attachments_content_store[attachment_id]]),
        media_type="application/octet-stream",
    )


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
