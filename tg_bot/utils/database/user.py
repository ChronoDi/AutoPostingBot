from typing import Union

from aiogram.types import Message
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.config_data import config
from tg_bot.database.models import User, Role


async def process_user(message: Message, session: AsyncSession) -> Role:
    result = await session.execute(select(User).where(User.tg_id == message.from_user.id))
    user: User = result.scalar_one_or_none()

    if user is None:
        role: Role = await create_user(message, session)
        return role
    else:
        await refresh_user(message, session, user)
        return user.role


async def get_admins(session: AsyncSession):
    result = await session.execute(select(User).where(or_(User.role == Role.ADMIN, User.role == Role.SUPER_ADMIN)))
    users = result.scalars().all()

    return users

async def refresh_user(message: Message, session: AsyncSession, user: User) -> None:
    user.first_name = message.from_user.first_name
    user.second_name = message.from_user.last_name
    user.user_name = message.from_user.username

    if user.tg_id in config.tg_bot.super_admin:
        user.role = Role.SUPER_ADMIN

    await session.commit()


async def create_user(message: Message, session: AsyncSession) -> Union[None, Role]:
    role = Role.SUPER_ADMIN if message.from_user.id in config.tg_bot.super_admin else Role.USER

    user = User(
        tg_id=message.from_user.id,
        first_name=message.from_user.first_name,
        second_name=message.from_user.last_name,
        user_name=message.from_user.username,
        role=role,
    )

    session.add(user)
    await session.commit()

    return role

async def get_user_by_id(session: AsyncSession, user_id) -> User:
    result = await session.execute(select(User).where(User.id == user_id))
    user: User = result.scalar_one_or_none()

    return user

async def get_user_by_tg_id(session: AsyncSession, tg_id) -> User:
    result = await session.execute(select(User).where(User.tg_id == tg_id))
    user: User = result.scalar_one_or_none()

    return user


async def change_role(session: AsyncSession, tg_id: int, role: Role)  -> None:
    user: User = await get_user_by_tg_id(session, tg_id)

    user.role = role
    await session.commit()


async def get_by_query(session: AsyncSession, query: str) -> list[User]:
    result = await session.execute(select(User).where(
                (User.first_name.ilike(f'%{query}%')) |
                (User.second_name.ilike(f'%{query}%')) |
                (User.user_name.ilike(f'%{query}%'))
            ))


    admins: list[User] = result.scalars().all()
    print(admins)

    return admins
