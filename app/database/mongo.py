from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from datetime import datetime
from app.models.mongo import (
    MongoEntry,
    MongoAttachmentMeta,
    MongoAttachmentContent,
    MongoRefreshToken,
    MongoSequence,
)


class MongoStore:
    def __init__(self, mongodb_url: str, db_name: str):
        self.client = AsyncIOMotorClient(mongodb_url)
        self.db = self.client[db_name]

    async def init_indexes(self):
        await self.db.entries.create_index("id", unique=True)
        await self.db.entries.create_index("revision")
        await self.db.attachments_meta.create_index("id", unique=True)
        await self.db.attachments_meta.create_index("revision")
        await self.db.attachments_content.create_index("id", unique=True)
        await self.db.refresh_tokens.create_index("token", unique=True)
        await self.db.sequences.create_index("name", unique=True)

    async def close(self):
        self.client.close()

    async def get_entry(self, entry_id: str) -> Optional[dict]:
        return await self.db.entries.find_one({"id": entry_id})

    async def upsert_entry(self, entry: MongoEntry) -> None:
        await self.db.entries.replace_one(
            {"id": entry.id},
            entry.dict(),
            upsert=True,
        )

    async def get_entries_since(self, since: int) -> list[dict]:
        cursor = self.db.entries.find({"revision": {"$gt": since}})
        return await cursor.to_list(length=None)

    async def get_attachment_meta(self, attachment_id: str) -> Optional[dict]:
        return await self.db.attachments_meta.find_one({"id": attachment_id})

    async def upsert_attachment_meta(self, meta: MongoAttachmentMeta) -> None:
        await self.db.attachments_meta.replace_one(
            {"id": meta.id},
            meta.dict(),
            upsert=True,
        )

    async def get_attachments_meta_since(self, since: int) -> list[dict]:
        cursor = self.db.attachments_meta.find({"revision": {"$gt": since}})
        return await cursor.to_list(length=None)

    async def get_attachment_content(self, attachment_id: str) -> Optional[dict]:
        return await self.db.attachments_content.find_one({"id": attachment_id})

    async def upsert_attachment_content(self, content: MongoAttachmentContent) -> None:
        await self.db.attachments_content.replace_one(
            {"id": content.id},
            content.dict(),
            upsert=True,
        )

    async def get_refresh_token(self, token: str) -> Optional[dict]:
        return await self.db.refresh_tokens.find_one({"token": token})

    async def create_refresh_token(self, token: MongoRefreshToken) -> None:
        await self.db.refresh_tokens.insert_one(token.dict())

    async def delete_refresh_token(self, token: str) -> None:
        await self.db.refresh_tokens.delete_one({"token": token})

    async def get_next_revision(self) -> int:
        sequence = await self.db.sequences.find_one_and_update(
            {"name": "_id"},
            {"$inc": {"value": 1}},
            upsert=True,
            return_document=True,
        )
        if sequence:
            return sequence["value"]
        else:
            await self.db.sequences.insert_one({"name": "_id", "value": 1})
            return 1

    async def get_latest_revision(self) -> int:
        sequence = await self.db.sequences.find_one({"name": "_id"})
        return sequence["value"] if sequence else 0
