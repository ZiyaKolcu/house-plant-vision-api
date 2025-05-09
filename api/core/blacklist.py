import redis.asyncio as redis

redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)


async def blacklist_token(token: str, expires_in: int):
    await redis_client.set(token, "blacklisted", ex=expires_in)


async def is_token_blacklisted(token: str) -> bool:
    result = await redis_client.get(token)
    return result == "blacklisted"
