from app.schemas.sync import (
    AttachmentMeta,
    EntryChange,
    PushRequest,
    PushResponse,
    SyncChangesResponse,
)
from app.state import InMemoryStore


class SyncService:
    def __init__(self, store: InMemoryStore):
        self.store = store

    def get_changes(self, since: int = 0) -> SyncChangesResponse:
        entry_changes = [
            EntryChange(**entry) for entry in self.store.entries.values() if entry["revision"] > since
        ]
        attachment_changes = [
            AttachmentMeta(**meta)
            for meta in self.store.attachments_meta.values()
            if meta["revision"] > since
        ]

        entry_changes.sort(key=lambda e: e.revision or 0)
        attachment_changes.sort(key=lambda a: a.revision or 0)

        return SyncChangesResponse(
            latestRevision=self.store.latest_revision,
            entries=entry_changes,
            attachments=attachment_changes,
        )

    def push_changes(self, payload: PushRequest) -> PushResponse:
        accepted: list[str] = []
        conflicts: list[str] = []
        missing_attachments: set[str] = set()

        for entry in payload.entries:
            existing = self.store.entries.get(entry.id)
            if existing and entry.revision is not None and entry.revision < existing["revision"]:
                conflicts.append(entry.id)
                continue

            current_revision = self.store.next_revision()
            entry_data = entry.dict()
            entry_data["revision"] = current_revision
            self.store.entries[entry.id] = entry_data
            accepted.append(entry.id)

            for att_id in entry.attachmentIds:
                if att_id not in self.store.attachments_content:
                    missing_attachments.add(att_id)

        for meta in payload.attachmentsMeta:
            existing_meta = self.store.attachments_meta.get(meta.id)
            if existing_meta and meta.revision is not None and meta.revision < existing_meta["revision"]:
                conflicts.append(meta.id)
                continue

            current_revision = self.store.next_revision()
            meta_data = meta.dict()
            meta_data["revision"] = current_revision
            self.store.attachments_meta[meta.id] = meta_data
            accepted.append(meta.id)

        return PushResponse(
            accepted=accepted,
            conflicts=conflicts,
            missingAttachments=sorted(missing_attachments),
        )
