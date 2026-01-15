import redis.asyncio as redis
from typing import Optional, Any
import json


class RedisCache:
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.client: Optional[redis.Redis] = None

    async def connect(self):
        self.client = await redis.from_url(self.redis_url, decode_responses=True)

    async def close(self):
        if self.client:
            await self.client.close()

    async def get(self, key: str) -> Optional[str]:
        if self.client:
            return await self.client.get(key)
        return None

    async def set(self, key: str, value: str, expire: Optional[int] = None) -> bool:
        if self.client:
            return await self.client.set(key, value, ex=expire)
        return False

    async def delete(self, key: str) -> bool:
        if self.client:
            return await self.client.delete(key) > 0
        return False

    async def get_json(self, key: str) -> Optional[Any]:
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                pass
        return None

    async def set_json(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        return await self.set(key, json.dumps(value), expire)

    async def exists(self, key: str) -> bool:
        if self.client:
            return await self.client.exists(key) > 0
        return False

    async def expire(self, key: str, seconds: int) -> bool:
        if self.client:
            return await self.client.expire(key, seconds)
        return False
