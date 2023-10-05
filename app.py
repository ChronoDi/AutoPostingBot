import asyncio
import datetime
import logging
from asyncio import Task

from aiogram import Bot, Dispatcher
from aioredis import Redis
from fluentogram import TranslatorHub
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from taskiq import TaskiqScheduler
from taskiq.api import run_receiver_task, run_scheduler_task
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_nats import NatsBroker

from tg_bot.config_data import config
from tg_bot.database.base import path
from tg_bot.lexicon.translator import get_hub
from tg_bot.meddleware import DbSessionMiddleware
from tg_bot.services.storage import init_storage
from tg_bot.handlers import router
from tg_bot.utils.cache.cache_access import CacheAccess
from tg_bot.utils.cache.groups import init_groups
from tg_bot.utils.sender import Sender
from tg_bot.utils.taskiq import TaskiqController

logger = logging.getLogger(__name__)


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format='%(filename)s:%(lineno)d #%(levelname)-8s'
                                                   '[%(asctime)s] - %(name)s - %(message)s')
    logger.info('Start bot')
    bot: Bot = Bot(config.tg_bot.token, parse_mode='HTML')
    redis: Redis = Redis(host=config.redis.host,
                         port=config.redis.port,
                         password=config.redis.password,
                         username=config.redis.user,
                         db=config.redis.db)
    cache = CacheAccess(redis)
    engine = create_async_engine(url=path, echo=False)
    dp: Dispatcher = Dispatcher(storage=init_storage(config.redis.is_need))
    session_maker = async_sessionmaker(engine, expire_on_commit=False)
    broker = NatsBroker([f'nats://{config.nats.host}:{config.nats.port}'])
    scheduler = TaskiqScheduler(broker=broker, sources=[LabelScheduleSource(broker)])
    sender = Sender(bot=bot, session_pool=session_maker)
    taskiq_controller = TaskiqController(broker=broker, scheduler=scheduler, sender=sender)
    await broker.startup()
    print(await taskiq_controller.get_all_tasks())
    t_hub: TranslatorHub = get_hub()
    dp.update.middleware(DbSessionMiddleware(session_pool=session_maker))
    dp.include_router(router)
    await taskiq_controller.init_mailing(session_pool=session_maker)
    worker_task = asyncio.create_task(run_receiver_task(broker))
    scheduler_task = asyncio.create_task(run_scheduler_task(scheduler))
    print(scheduler_task)

    await init_groups(cache, session_maker, bot)
    await bot.delete_webhook(drop_pending_updates=True)

    try:
        await dp.start_polling(bot, cache=cache, _translator_hub=t_hub, taskiq_controller=taskiq_controller,
                               worker_task=worker_task, scheduler_task=scheduler_task, broker=broker)
    except KeyboardInterrupt:
        logger.info(f'**** Bot is shutdown in {datetime.datetime.now()}')
    finally:
        worker_task.cancel()
        scheduler_task.cancel()
        await broker.shutdown()


if __name__ == '__main__':
    asyncio.run(main())
