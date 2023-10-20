from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.database.models import Group


async def add_group(session: AsyncSession, tg_id: int, group_type: str, title: str, is_active: bool = True):
    group = Group(tg_id=tg_id, type=group_type, title=title, is_active=is_active)

    session.add(group)
    await session.commit()



async def edit_group(session: AsyncSession, old_tg_id: int, new_tg_int: int, new_type: str):
    result = await session.execute(select(Group).where(Group.tg_id == old_tg_id))
    group: Group = result.scalar_one_or_none()

    group.tg_id = new_tg_int
    group.type = new_type

    await session.commit()


async def get_all_active_groups(session: AsyncSession):
    result = await session.execute(select(Group).where(Group.is_active == True))
    groups = result.scalars().all()

    return groups


async def get_group_by_tg_id(session: AsyncSession, group_tg_id):
    result = await session.execute(select(Group).where(Group.tg_id == group_tg_id))
    group: Group = result.scalar_one_or_none()

    return group


async def change_active(session: AsyncSession, group: Group, is_active: bool):
    group.is_active = is_active

    await session.commit()
