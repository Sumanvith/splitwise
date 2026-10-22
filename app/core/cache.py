import json

import redis.asyncio as redis

from app.config import settings

redis_client = redis.from_url(
    settings.redis_url,
    decode_responses=True,
    socket_connect_timeout=1,
    socket_timeout=1,
)


def balances_key(group_id: int) -> str:
    return f"balances:{group_id}"


async def cache_get(key: str):
    try:
        value = await redis_client.get(key)
        return json.loads(value) if value else None
    except Exception:
        return None


async def cache_set(key: str, value, ttl: int = 60):
    try:
        await redis_client.set(key, json.dumps(value), ex=ttl)
    except Exception:
        pass


async def cache_delete(key: str):
    try:
        await redis_client.delete(key)
    except Exception:
        pass
