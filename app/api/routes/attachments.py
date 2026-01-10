from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import StreamingResponse

from app.api.deps import get_store, require_auth
from app.schemas.errors import ErrorResponse
from app.services.attachments import AttachmentService
from app.state import InMemoryStore

router = APIRouter(prefix="/attachments", tags=["attachments"])


def get_attachment_service(store: InMemoryStore = Depends(get_store)) -> AttachmentService:
    return AttachmentService(store)


@router.put(
    "/{attachment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={401: {"model": ErrorResponse}},
)
async def upload_attachment(
    attachment_id: str,
    request: Request,
    token: str = Depends(require_auth),
    attachment_service: AttachmentService = Depends(get_attachment_service),
):
    del token
    body = await request.body()
    attachment_service.upload(attachment_id, body)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/{attachment_id}",
    responses={
        200: {"content": {"application/octet-stream": {}}},
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
async def download_attachment(
    attachment_id: str,
    token: str = Depends(require_auth),
    attachment_service: AttachmentService = Depends(get_attachment_service),
):
    del token
    content = attachment_service.download(attachment_id)
    return StreamingResponse(content=iter([content]), media_type="application/octet-stream")
