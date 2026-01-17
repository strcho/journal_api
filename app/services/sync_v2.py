from app.schemas.sync import (
    AttachmentMeta,
    EntryChange,
    PushRequest,
    PushResponse,
    SyncChangesResponse,
)
from app.schemas.journal import JournalChange
from app.database.mongo import MongoStore
from app.models.mongo import MongoEntry, MongoAttachmentMeta, MongoJournal


class SyncService:
    def __init__(self, store: MongoStore):
        self.store = store

    async def get_changes(self, since: int = 0) -> SyncChangesResponse:
        entry_docs = await self.store.get_entries_since(since)
        attachment_docs = await self.store.get_attachments_meta_since(since)
        journal_docs = await self.store.get_journals_since(since)

        entry_changes = [
            EntryChange(
                id=doc["id"],
                journalId=doc["journal_id"],
                payloadEncrypted=doc["payload_encrypted"],
                payloadVersion=doc["payload_version"],
                attachmentIds=doc["attachment_ids"],
                createdAt=doc["created_at"],
                updatedAt=doc["updated_at"],
                deletedAt=doc.get("deleted_at"),
                revision=doc.get("revision"),
            )
            for doc in entry_docs
        ]
        attachment_changes = [
            AttachmentMeta(
                id=doc["id"],
                sha256=doc["sha256"],
                sizeBytes=doc["size_bytes"],
                mimeType=doc["mime_type"],
                createdAt=doc["created_at"],
                updatedAt=doc["updated_at"],
                deletedAt=doc.get("deleted_at"),
                revision=doc.get("revision"),
            )
            for doc in attachment_docs
        ]
        journal_changes = [
            JournalChange(
                id=doc["id"],
                name=doc["name"],
                color=doc.get("color"),
                createdAt=doc["created_at"],
                updatedAt=doc["updated_at"],
                deletedAt=doc.get("deleted_at"),
                revision=doc.get("revision"),
            )
            for doc in journal_docs
        ]

        entry_changes.sort(key=lambda e: e.revision or 0)
        attachment_changes.sort(key=lambda a: a.revision or 0)
        journal_changes.sort(key=lambda j: j.revision or 0)

        latest_revision = await self.store.get_latest_revision()

        return SyncChangesResponse(
            latestRevision=latest_revision,
            entries=entry_changes,
            attachments=attachment_changes,
            journals=journal_changes,
        )

    async def push_changes(self, payload: PushRequest) -> PushResponse:
        accepted: list[str] = []
        conflicts: list[str] = []
        missing_attachments: set[str] = set()

        for entry in payload.entries:
            existing = await self.store.get_entry(entry.id)
            if existing and entry.revision is not None and entry.revision < existing.get(
                "revision", 0
            ):
                conflicts.append(entry.id)
                continue

            current_revision = await self.store.get_next_revision()
            mongo_entry = MongoEntry(
                id=entry.id,
                journal_id=entry.journalId,
                payload_encrypted=entry.payloadEncrypted,
                payload_version=entry.payloadVersion,
                attachment_ids=entry.attachmentIds,
                created_at=entry.createdAt,
                updated_at=entry.updatedAt,
                deleted_at=entry.deletedAt,
                revision=current_revision,
            )
            await self.store.upsert_entry(mongo_entry)
            accepted.append(entry.id)

            for att_id in entry.attachmentIds:
                content = await self.store.get_attachment_content(att_id)
                if not content:
                    missing_attachments.add(att_id)

        for meta in payload.attachmentsMeta:
            existing_meta = await self.store.get_attachment_meta(meta.id)
            if existing_meta and meta.revision is not None and meta.revision < existing_meta.get(
                "revision", 0
            ):
                conflicts.append(meta.id)
                continue

            current_revision = await self.store.get_next_revision()
            mongo_meta = MongoAttachmentMeta(
                id=meta.id,
                sha256=meta.sha256,
                size_bytes=meta.sizeBytes,
                mime_type=meta.mimeType,
                created_at=meta.createdAt,
                updated_at=meta.updatedAt,
                deleted_at=meta.deletedAt,
                revision=current_revision,
            )
            await self.store.upsert_attachment_meta(mongo_meta)
            accepted.append(meta.id)

        for journal in payload.journals:
            existing_journal = await self.store.get_journal(journal.id)
            if (existing_journal and journal.revision is not None
                    and journal.revision < existing_journal.get("revision", 0)):
                conflicts.append(journal.id)
                continue

            current_revision = await self.store.get_next_revision()
            mongo_journal = MongoJournal(
                id=journal.id,
                name=journal.name,
                color=journal.color,
                created_at=journal.createdAt,
                updated_at=journal.updatedAt,
                deleted_at=journal.deletedAt,
                revision=current_revision,
            )
            await self.store.upsert_journal(mongo_journal)
            accepted.append(journal.id)

        return PushResponse(
            accepted=accepted,
            conflicts=conflicts,
            missingAttachments=sorted(missing_attachments),
        )
