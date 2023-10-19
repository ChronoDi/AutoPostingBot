from typing import Any
from redis.asyncio import Redis


class CacheAccess:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get_list(self, value: str) -> list[Any]:
        need_list: list[Any] = []
        values = await self.redis.lrange(value, 0, 1)

        for value in values:
            need_list.append(value.decode())

        return need_list


    async def get_dict(self, name: str) -> dict[str, str]:
        need_dict: dict[str: str] = {}
        values = await self.redis.hgetall(name)

        for key, value in values.items():
            need_dict.update({key.decode() : value.decode()})

        return need_dict


    async def add_to_list(self, name: str, value: str):
        await self.redis.rpush(name, value)


    async def remove_from_list(self, name: str, value: str):
        await self.redis.lrem(name, count=0, value=value)


    async def add_to_dict(self, name: str, key: str, value: str):
        await self.redis.hset(name, key, value)


    async def remove_from_dict(self, name: str, *keys: str):
        await self.redis.hdel(name, *keys)


    async def check_entity(self, name):
        result = await self.redis.exists(name)

        return result


    async def flush_cache(self):
        await self.redis.flushdb()

