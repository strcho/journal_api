import uuid
from datetime import datetime

from app.schemas.journal import CreateJournalRequest, UpdateJournalRequest, Journal
from app.database.mongo import MongoStore
from app.models.mongo import MongoJournal
from app.core.errors import http_error
from fastapi import status


DEFAULT_JOURNAL_UUID = "00000000-0000-0000-0000-000000000001"
DEFAULT_JOURNAL_NAME = "日常"


class JournalService:
    def __init__(self, store: MongoStore):
        self.store = store

    async def get_default_journal(self) -> Journal:
        default_journal = await self.store.get_journal(DEFAULT_JOURNAL_UUID)
        if default_journal:
            deleted_at = default_journal.get("deleted_at")
            return Journal(
                id=default_journal["id"],
                name=default_journal["name"],
                color=default_journal.get("color"),
                createdAt=default_journal["created_at"].isoformat(),
                updatedAt=default_journal["updated_at"].isoformat(),
                deletedAt=deleted_at.isoformat() if deleted_at else None,
                revision=default_journal.get("revision"),
            )

        return await self._create_default_journal()

    async def _create_default_journal(self) -> Journal:
        revision = await self.store.get_next_revision()
        now = datetime.utcnow()
        journal = MongoJournal(
            id=DEFAULT_JOURNAL_UUID,
            name=DEFAULT_JOURNAL_NAME,
            color=None,
            created_at=now,
            updated_at=now,
            deleted_at=None,
            revision=revision,
        )
        await self.store.upsert_journal(journal)
        return Journal(
            id=journal.id,
            name=journal.name,
            color=journal.color,
            createdAt=journal.created_at.isoformat(),
            updatedAt=journal.updated_at.isoformat(),
            deletedAt=None,
            revision=journal.revision,
        )

    async def create_journal(self, payload: CreateJournalRequest) -> Journal:
        revision = await self.store.get_next_revision()
        now = datetime.utcnow()
        journal_id = str(uuid.uuid4())

        journal = MongoJournal(
            id=journal_id,
            name=payload.name,
            color=payload.color,
            created_at=now,
            updated_at=now,
            deleted_at=None,
            revision=revision,
        )
        await self.store.upsert_journal(journal)

        return Journal(
            id=journal.id,
            name=journal.name,
            color=journal.color,
            createdAt=journal.created_at.isoformat(),
            updatedAt=journal.updated_at.isoformat(),
            deletedAt=None,
            revision=journal.revision,
        )

    async def update_journal(
        self, journal_id: str, payload: UpdateJournalRequest
    ) -> Journal:
        existing = await self.store.get_journal(journal_id)
        if not existing:
            raise http_error(
                code="JOURNAL_NOT_FOUND",
                message="Journal not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        if journal_id == DEFAULT_JOURNAL_UUID and payload.name:
            raise http_error(
                code="DEFAULT_JOURNAL_NAME_IMMUTABLE",
                message="Default journal name cannot be changed.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        revision = await self.store.get_next_revision()
        now = datetime.utcnow()

        updated_journal = MongoJournal(
            id=journal_id,
            name=payload.name if payload.name is not None else existing["name"],
            color=payload.color if payload.color is not None else existing.get("color"),
            created_at=existing["created_at"],
            updated_at=now,
            deleted_at=existing.get("deleted_at"),
            revision=revision,
        )
        await self.store.upsert_journal(updated_journal)

        return Journal(
            id=updated_journal.id,
            name=updated_journal.name,
            color=updated_journal.color,
            createdAt=updated_journal.created_at.isoformat(),
            updatedAt=updated_journal.updated_at.isoformat(),
            deletedAt=updated_journal.deleted_at.isoformat()
            if updated_journal.deleted_at
            else None,
            revision=updated_journal.revision,
        )

    async def delete_journal(self, journal_id: str) -> None:
        if journal_id == DEFAULT_JOURNAL_UUID:
            raise http_error(
                code="DEFAULT_JOURNAL_IMMUTABLE",
                message="Default journal cannot be deleted.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        existing = await self.store.get_journal(journal_id)
        if not existing:
            raise http_error(
                code="JOURNAL_NOT_FOUND",
                message="Journal not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        if existing.get("deleted_at"):
            return

        revision = await self.store.get_next_revision()
        now = datetime.utcnow()

        updated_journal = MongoJournal(
            id=journal_id,
            name=existing["name"],
            color=existing.get("color"),
            created_at=existing["created_at"],
            updated_at=now,
            deleted_at=now,
            revision=revision,
        )
        await self.store.upsert_journal(updated_journal)

    async def list_journals(self) -> list[Journal]:
        journal_docs = await self.store.get_all_journals()
        return [
            Journal(
                id=doc["id"],
                name=doc["name"],
                color=doc.get("color"),
                createdAt=doc["created_at"].isoformat(),
                updatedAt=doc["updated_at"].isoformat(),
                deletedAt=doc.get("deleted_at").isoformat()
                if doc.get("deleted_at")
                else None,
                revision=doc.get("revision"),
            )
            for doc in journal_docs
        ]
