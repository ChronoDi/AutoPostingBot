import asyncio
import logging

from aiogram import Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis
from fluentogram import TranslatorHub

from bot import bot
from tg_bot.config_data import config
from tg_bot.database.base import session_maker
from tg_bot.lexicon.translator import get_hub
from tg_bot.meddleware import DbSessionMiddleware
from tg_bot.handlers import router
from tg_bot.utils.cache.cache_access import CacheAccess
from tg_bot.utils.cache.groups import init_groups
from tg_bot.utils.process_user import init_admins
from tkq import broker


logger = logging.getLogger(__name__)
redis: Redis = Redis(host=config.redis.host,
                     port=config.redis.port,
                     password=config.redis.password,
                     username=config.redis.user,
                     db=config.redis.db)
dp: Dispatcher = Dispatcher(storage=RedisStorage(redis))


@dp.startup()
async def setup_taskiq():
    if not broker.is_worker_process:
        logging.info("Setting up taskiq")
        await broker.startup()


@dp.shutdown()
async def shutdown_taskiq():
    if not broker.is_worker_process:
        logging.info("Shutting down taskiq")
        await broker.shutdown()


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format='%(filename)s:%(lineno)d #%(levelname)-8s'
                                                   '[%(asctime)s] - %(name)s - %(message)s')
    logger.info('Start bot')
    cache = CacheAccess(redis)
    t_hub: TranslatorHub = get_hub()
    dp.update.middleware(DbSessionMiddleware(session_pool=session_maker))
    dp.include_router(router)

    async with session_maker() as session:
        await init_groups(cache, session, bot)

    await init_admins(cache=cache, session_pool=session_maker)
    await bot.delete_webhook(drop_pending_updates=True)

    try:
        await dp.start_polling(bot, cache=cache, _translator_hub=t_hub)
    except KeyboardInterrupt:
        logger.info(f'**** Bot is shutdown')


if __name__ == '__main__':
    asyncio.run(main())
