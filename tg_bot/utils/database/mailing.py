from datetime import datetime
from typing import Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from tg_bot.database.models import Mailing


async def get_all_mailing(session: AsyncSession):
    result = await session.execute(select(Mailing))
    mailing = result.scalars().all()

    return mailing


async def create_mailing(year: int, month: int, day: int, hour: int, minute: int,
                         group_id: int, name: str, session: AsyncSession):
    mailing = Mailing(
        name=name,
        mailing_date=datetime(year, month, day, hour, minute),
        group_id=group_id,
    )

    session.add(mailing)
    await session.commit()

    return mailing.mailing_date, mailing.id


async def get_mailing_by_id(session: AsyncSession, mailing_id: int):
    result = await session.execute(select(Mailing).where(Mailing.id == mailing_id))
    mailing: Mailing = result.scalar_one_or_none()

    return mailing


async def set_group(session: AsyncSession, mailing_id: int, new_group_id: int):
    mailing: Mailing = await get_mailing_by_id(session, mailing_id)

    mailing.group_id = new_group_id
    await session.commit()


async def set_time(session: AsyncSession, mailing_id: int, new_date: datetime):
    mailing: Mailing = await get_mailing_by_id(session, mailing_id)

    mailing.mailing_date = new_date
    await session.commit()

    return mailing.task_id


async def change_post_count(session: AsyncSession, mailing_id, is_increase: bool = True):
    result = await session.execute(select(Mailing).where(Mailing.id == mailing_id))
    mailing: Mailing = result.scalar_one_or_none()

    mailing.count_posts = mailing.count_posts + 1 if is_increase else mailing.count_posts - 1
    await session.commit()


async def remove_mailing(session: AsyncSession, mailing_id: int):
    mailing = await get_mailing_by_id(session, mailing_id)
    await session.delete(mailing)
    await session.commit()

    return mailing.task_id


def sync_get_mailing_by_id(session: Session, mailing_id: int) -> Union[None, Mailing]:
    mailing: Mailing = session.execute(select(Mailing).where(Mailing.id == mailing_id)).scalar_one_or_none()

    return mailing


def sync_delete_mailing(session: Session, mailing: Mailing) -> None:
    session.delete(mailing)
    session.commit()


def mark_sent(session: Session, mailing: Mailing) -> None:
    mailing.is_sent = True
    session.add(mailing)
    session.commit()


async def add_task_id(session: AsyncSession, mailing_id: int, task_id: int):
    mailing: Mailing = await get_mailing_by_id(session, mailing_id)
    mailing.task_id = task_id
    await session.commit()


async def get_mailing_by_group_id(session: AsyncSession, group_id: int):
    result = await session.execute(select(Mailing).where(Mailing.group_id == group_id))
    mailing: list[Mailing] = result.scalars().all()

    return mailing



