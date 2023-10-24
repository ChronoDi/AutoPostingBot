import logging
from typing import Union

from aiogram.types import Message
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from tg_bot.config_data import config
from tg_bot.database.models import Role, User
from tg_bot.utils.cache.cache_access import CacheAccess
from tg_bot.utils.cache.literals import cache_names
from tg_bot.utils.database.user import process_user, get_admins, get_user_by_id, change_role, get_user_by_tg_id, \
    get_by_query


async def init_admins(session_pool: async_sessionmaker, cache: CacheAccess) -> None:
    async with session_pool() as session:
        admins: list[User] = await get_admins(session)

        for admin in admins:
            if admin.role == Role.SUPER_ADMIN and not admin.tg_id in config.tg_bot.super_admin:
                await change_role(session, admin.tg_id, Role.ADMIN)

            await cache.add_to_dict(cache_names.ADMINS, str(admin.tg_id), '1')


async def register_user(message: Message, session: AsyncSession, cache: CacheAccess) -> None:
    role: Role = await process_user(message, session)

    access: str = '1' if (role == Role.ADMIN or role == Role.SUPER_ADMIN) else '0'
    await cache.add_to_dict(cache_names.ADMINS, str(message.from_user.id), access)
    logging.info(f'A user by name "{message.from_user.first_name} {message.from_user.last_name} ({message.from_user.username})" '
                 f'with an id "{message.from_user.id}" has been registered')



async def get_admins_id(session: AsyncSession) -> list[int]:
    admins_id: list[int] = []
    users = await get_admins(session)

    for user in users:
        admins_id.append(user.tg_id)

    return admins_id


async def get_admins_dict(session: AsyncSession) -> dict[str, str]:
    dict_admins: dict[str, str] = {}
    admins: list[User] = await get_admins(session)

    for admin in admins:
        name = init_user_name(admin)
        dict_admins.update({str(admin.id) : name[:30]})

    return dict_admins


def init_user_name(user: User) -> str:
    name: str = user.first_name if user.first_name else ''
    name = name + (user.second_name if user.second_name else '')
    name = name + (f' ({user.user_name})' if user.user_name else '')

    return name


async def get_user_tg_id(session: AsyncSession, tg_id: int) -> Union[User, None]:
    user: User = await get_user_by_tg_id(session, tg_id)

    if user.role == Role.SUPER_ADMIN or user.role == Role.ADMIN:
        return None

    return user


async def get_user(session: AsyncSession, user_id: int) -> User:
    user: User = await get_user_by_id(session, user_id)

    return user


async def get_users_by_query(session: AsyncSession, query: str) -> list[User]:
    users: list[User] = await get_by_query(session, query)

    return users


async def change_user_role(session: AsyncSession, cache: CacheAccess, tg_id: int, role: Role) -> None:
    await change_role(session, tg_id, role)
    access = '1' if role == role.ADMIN else '0'
    await cache.add_to_dict(cache_names.ADMINS, str(tg_id), access)
    logging.info(f'The user with the id {tg_id} changed the access level to {access}')


async def show_users(list_users: list[User], lexicon: TranslatorRunner) -> str:
    result: str = ''

    for i in range(0, len(list_users)):
        result += f'{i + 1}\n' + lexicon.user.info() + '\n\n'

    return result


