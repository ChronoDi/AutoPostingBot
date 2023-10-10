from aiogram.fsm.storage.base import BaseStorage
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
# from aioredis import Redis
from redis.asyncio import Redis

from tg_bot.config_data import config


def init_storage(is_redis: bool) -> BaseStorage:
    if is_redis:
        return RedisStorage(redis=Redis(host=config.redis.host,
                                        port=config.redis.port,
                                        password=config.redis.password,
                                        username=config.redis.user,
                                        db=0))

    return MemoryStorage()
