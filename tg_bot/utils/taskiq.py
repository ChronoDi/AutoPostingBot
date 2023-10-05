import logging
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import async_sessionmaker
from taskiq import TaskiqScheduler
from taskiq_nats import NatsBroker

from tg_bot.database.models import Mailing
from tg_bot.utils.database.mailing import get_all_mailing
from tg_bot.utils.process_mailing import process_remove_mailing
from tg_bot.utils.sender import Sender


class TaskiqController:

    def __init__(self, broker: NatsBroker, scheduler: TaskiqScheduler, sender: Sender):
        self._broker = broker
        self._scheduler = scheduler
        self._sender = sender


    async def register_mailing(self, mailing_id: str, group_id: int, date: datetime):
        self._broker.register_task(
            func=self._sender.send_mailing,
            task_name=mailing_id,
            schedule=[
                {
                    "time": date.astimezone(timezone.utc),
                    "args": [int(mailing_id), group_id],
                },
            ],
        )

        logging.info(f'****** A task "{mailing_id}" to group {group_id} has been created for the date "{date}"')

    async def change_date(self, mailing_id: str, new_date: datetime) -> None:
        task = self._broker.find_task(mailing_id)
        task.labels.get('schedule')[0].update({'time': new_date.astimezone(timezone.utc)})
        logging.info(f'****** The task "{mailing_id}" date has been updated to "{new_date}"')


    async def remove_mailing(self, mailing_id: str) -> None:
        task = self._broker.find_task(mailing_id)
        task.labels.clear()
        logging.info(f'****** The task "{mailing_id}" was removed"')


    async def get_all_tasks(self):
        return self._broker.get_all_tasks()


    async def init_mailing(self, session_pool: async_sessionmaker) -> None:
        async with session_pool() as session:
            mailing_list: list[Mailing] = await get_all_mailing(session)

            for mailing in mailing_list:
                if mailing.mailing_date > datetime.now():
                    await self.register_mailing(str(mailing.id), mailing.group_id, mailing.mailing_date)
                else:
                    await process_remove_mailing(session, mailing.id)
