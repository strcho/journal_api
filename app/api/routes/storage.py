from fastapi import APIRouter, Depends

from app.api.deps import get_store
from app.schemas.errors import ErrorResponse
from app.schemas.storage import QiniuTokenResponse
from app.services.qiniu import QiniuService
from app.state import InMemoryStore

router = APIRouter(prefix="/storage", tags=["storage"])


def get_qiniu_service() -> QiniuService:
    return QiniuService()


@router.get(
    "/qiniu/token",
    response_model=QiniuTokenResponse,
    responses={401: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def get_qiniu_upload_token(
    key: str,
    qiniu_service: QiniuService = Depends(get_qiniu_service),
):
    """Get Qiniu upload token for a specific key."""
    upload_token = qiniu_service.generate_upload_token(key)
    return QiniuTokenResponse(uploadToken=upload_token)
