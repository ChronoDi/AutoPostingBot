from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.database.models import Group


async def add_group(session: AsyncSession, tg_id: int, group_type: str, title: str):
    group = Group(tg_id=tg_id, type=group_type, title=title)

    session.add(group)
    await session.commit()


async def remove_group(session: AsyncSession, tg_id: int):
    result = await session.execute(select(Group).where(Group.tg_id==tg_id))
    group = result.scalar()

    await session.delete(group)
    await session.commit()


async def edit_group(session: AsyncSession, old_tg_id: int, new_tg_int: int, new_type: str):
    result = await session.execute(select(Group).where(Group.tg_id == old_tg_id))
    group: Group = result.scalar_one_or_none()

    group.tg_id = new_tg_int
    group.type = new_type

    await session.commit()


async def get_all_groups(session: AsyncSession):
    result = await session.execute(select(Group))
    groups = result.scalars().all()

    return groups

async def get_group_by_tg_id(session: AsyncSession, group_tg_id):
    result = await session.execute(select(Group).where(Group.tg_id == group_tg_id))
    group: Group = result.scalar_one_or_none()

    return group
