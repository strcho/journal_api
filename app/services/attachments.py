from fastapi import status

from app.core.errors import http_error
from app.state import InMemoryStore


class AttachmentService:
    def __init__(self, store: InMemoryStore):
        self.store = store

    def upload(self, attachment_id: str, content: bytes) -> None:
        self.store.attachments_content[attachment_id] = content

    def download(self, attachment_id: str) -> bytes:
        if attachment_id not in self.store.attachments_content:
            raise http_error(
                code="RESOURCE_NOT_FOUND",
                message="Attachment not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        return self.store.attachments_content[attachment_id]
