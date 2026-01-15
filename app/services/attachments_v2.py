from fastapi import status

from app.core.errors import http_error
from app.database.mongo import MongoStore


class AttachmentService:
    def __init__(self, store: MongoStore):
        self.store = store

    async def upload(self, attachment_id: str, content: bytes) -> None:
        from app.models.mongo import MongoAttachmentContent
        from datetime import datetime

        mongo_content = MongoAttachmentContent(
            id=attachment_id,
            content=content,
        )
        await self.store.upsert_attachment_content(mongo_content)

    async def download(self, attachment_id: str) -> bytes:
        doc = await self.store.get_attachment_content(attachment_id)
        if not doc:
            raise http_error(
                code="RESOURCE_NOT_FOUND",
                message="Attachment not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        return doc["content"]
