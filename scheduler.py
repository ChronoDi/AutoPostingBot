import json, pytz
from datetime import datetime
from typing import List, Any

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
from taskiq import ScheduleSource, ScheduledTask
from taskiq.kicker import AsyncKicker

from tg_bot.database.models import DbSchedule


class DbScheduleSource(ScheduleSource):

    def __init__(self, engine: AsyncEngine):
        self.engine = engine

    async def get_schedules(self) -> List[ScheduledTask]:
        async with AsyncSession(self.engine) as session:
            result = await session.execute(select(DbSchedule))
            schedules = result.scalars().all()

            return [
                ScheduledTask(
                    source=self,
                    task_name=s.task_name,
                    args=s.args,
                    kwargs=json.loads(s.kwargs),
                    labels={"_sched_id": s.id, **json.loads(s.labels)},
                    time=s.time
                )
                for s in schedules
            ]

    async def add_task(
            self,
            task: AsyncKicker[Any, Any],
            time: datetime,
            *args: Any,
            **kwargs: Any
    ) -> None:
        schedule = DbSchedule(
            task_name=task.task_name,
            args=json.dumps(list(args)),
            kwargs=json.dumps(kwargs),
            labels=json.dumps(task.labels),
            time=time.astimezone(pytz.UTC).replace(tzinfo=None)
        )
        async with AsyncSession(self.engine) as session:
            session.add(schedule)
            await session.commit()

    async def remove_schedule(self, schedule_id: int) -> None:
        async with AsyncSession(self.engine) as session:
            await session.execute(
                delete(DbSchedule).where(DbSchedule.id == schedule_id)
            )
            await session.commit()

    async def post_send(self, task: ScheduledTask) -> None:
        schedule_id = task.labels.get("_sched_id")
        if schedule_id is None:
            return

        async with AsyncSession(self.engine) as session:
            await session.execute(
                delete(DbSchedule).where(DbSchedule.id == schedule_id)
            )
            await session.commit()


    async def reschedule_task(self, schedule_id: int, new_time: datetime) -> None:

        async with AsyncSession(self.engine) as session:
            schedule = await session.get(DbSchedule, schedule_id)
            if not schedule:
                raise ValueError(f"Schedule {schedule_id} not found")

            schedule.time = new_time
            session.add(schedule)
            await session.commit()