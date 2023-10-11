import taskiq_aiogram
from taskiq import TaskiqScheduler
from taskiq_redis import ListQueueBroker

from tg_bot.database.base import engine
from scheduler import DbScheduleSource

from tg_bot.config_data import config

broker = ListQueueBroker(
    url=f"redis://{config.redis.host}:{config.redis.port}/2",
    queue_name='mailing'
)

db_source = DbScheduleSource(engine=engine)

taskiq_aiogram.init(
    broker,
    "app:dp",
    "bot:bot",
)

sched = TaskiqScheduler(
    broker,
    sources=[db_source],
    refresh_delay=20,
)

