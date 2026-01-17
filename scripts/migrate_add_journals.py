import os
import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

DEFAULT_JOURNAL_UUID = "00000000-0000-0000-0000-000000000001"
DEFAULT_JOURNAL_NAME = "日常"


async def migrate():
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    db_name = os.getenv("MONGODB_DB_NAME", "journal_db")

    client = AsyncIOMotorClient(mongodb_url)
    db = client[db_name]

    print(f"Connected to MongoDB at {mongodb_url}, database: {db_name}")

    # 1. Create default journal if not exists
    default_journal = await db.journals.find_one({"id": DEFAULT_JOURNAL_UUID})
    if not default_journal:
        now = datetime.utcnow()
        print(f"Creating default journal: {DEFAULT_JOURNAL_NAME}")
        await db.journals.insert_one(
            {
                "id": DEFAULT_JOURNAL_UUID,
                "name": DEFAULT_JOURNAL_NAME,
                "color": None,
                "created_at": now,
                "updated_at": now,
                "deleted_at": None,
                "revision": 1,
            }
        )
        print("Default journal created")
    else:
        print(f"Default journal already exists: {default_journal['name']}")

    # 2. Update entries without journal_id
    entries_without_journal = await db.entries.find({"journal_id": {"$exists": False}}).to_list(length=None)
    print(f"Found {len(entries_without_journal)} entries without journal_id")

    if entries_without_journal:
        for entry in entries_without_journal:
            await db.entries.update_one(
                {"_id": entry["_id"]},
                {"$set": {"journal_id": DEFAULT_JOURNAL_UUID}}
            )
        print(f"Updated {len(entries_without_journal)} entries with default journal_id")
    else:
        print("No entries need to be updated")

    # 3. Create indexes
    await db.journals.create_index("id", unique=True)
    await db.journals.create_index("revision")
    await db.entries.create_index("journal_id")
    print("Indexes created")

    client.close()
    print("Migration completed successfully!")


if __name__ == "__main__":
    asyncio.run(migrate())
