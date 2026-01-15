from app.schemas.sync import (
    AttachmentMeta,
    EntryChange,
    PushRequest,
    PushResponse,
    SyncChangesResponse,
)
from app.database.mongo import MongoStore
from app.models.mongo import MongoEntry, MongoAttachmentMeta


class SyncService:
    def __init__(self, store: MongoStore):
        self.store = store

    async def get_changes(self, since: int = 0) -> SyncChangesResponse:
        entry_docs = await self.store.get_entries_since(since)
        attachment_docs = await self.store.get_attachments_meta_since(since)

        entry_changes = [
            EntryChange(
                id=doc["id"],
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

        entry_changes.sort(key=lambda e: e.revision or 0)
        attachment_changes.sort(key=lambda a: a.revision or 0)

        latest_revision = await self.store.get_latest_revision()

        return SyncChangesResponse(
            latestRevision=latest_revision,
            entries=entry_changes,
            attachments=attachment_changes,
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
                payloadEncrypted=entry.payloadEncrypted,
                payloadVersion=entry.payloadVersion,
                attachmentIds=entry.attachmentIds,
                createdAt=entry.createdAt,
                updatedAt=entry.updatedAt,
                deletedAt=entry.deletedAt,
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
                sizeBytes=meta.sizeBytes,
                mimeType=meta.mimeType,
                createdAt=meta.createdAt,
                updatedAt=meta.updatedAt,
                deletedAt=meta.deletedAt,
                revision=current_revision,
            )
            await self.store.upsert_attachment_meta(mongo_meta)
            accepted.append(meta.id)

        return PushResponse(
            accepted=accepted,
            conflicts=conflicts,
            missingAttachments=sorted(missing_attachments),
        )
