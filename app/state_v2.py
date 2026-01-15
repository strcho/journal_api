from app.database.mongo import MongoStore
from app.database.redis import RedisCache
from typing import Optional

_mongo_store: Optional[MongoStore] = None
_redis_cache: Optional[RedisCache] = None


async def init_databases(mongodb_url: str, db_name: str, redis_url: str):
    global _mongo_store, _redis_cache

    _mongo_store = MongoStore(mongodb_url, db_name)
    await _mongo_store.init_indexes()

    _redis_cache = RedisCache(redis_url)
    await _redis_cache.connect()


async def close_databases():
    global _mongo_store, _redis_cache

    if _mongo_store:
        await _mongo_store.close()
    if _redis_cache:
        await _redis_cache.close()


async def get_mongo_store() -> MongoStore:
    if _mongo_store is None:
        raise RuntimeError("MongoDB store not initialized. Call init_databases first.")
    return _mongo_store


async def get_redis_cache() -> RedisCache:
    if _redis_cache is None:
        raise RuntimeError("Redis cache not initialized. Call init_databases first.")
    return _redis_cache
