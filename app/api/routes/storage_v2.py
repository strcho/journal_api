from fastapi import APIRouter, Depends

from app.api.deps_v2 import require_auth, get_redis_cache_dep
from app.schemas.errors import ErrorResponse
from app.schemas.storage import QiniuTokenResponse
from app.services.qiniu import QiniuService

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
    token: str = Depends(require_auth),
    qiniu_service: QiniuService = Depends(get_qiniu_service),
):
    del token
    upload_token = qiniu_service.generate_upload_token(key)
    return QiniuTokenResponse(uploadToken=upload_token)
