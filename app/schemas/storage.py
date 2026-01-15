from pydantic import BaseModel


class QiniuTokenResponse(BaseModel):
    uploadToken: str
