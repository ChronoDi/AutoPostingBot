from aiogram.types import Message
from aiogram.filters import BaseFilter
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.utils.cache.cache_access import CacheAccess
from tg_bot.utils.cache.literals import cache_names
from tg_bot.utils.process_user import get_admins_id
from tg_bot.config_data import config


class IsAdmin(BaseFilter):
    keyword = 'is_admin'

    async def __call__(self, message: Message, session: AsyncSession, cache: CacheAccess) -> bool:
        cache_admins: dict[str, str] = await cache.get_dict(cache_names.ADMINS)
        cache_exist = await cache.check_entity(cache_names.ADMINS)

        if str(message.from_user.id) not in cache_admins or not cache_exist:
            admins_id: list[int] = await get_admins_id(session)
            access: str = '1' if message.from_user.id in admins_id else '0'
            await cache.add_to_dict(cache_names.ADMINS, str(message.from_user.id), access)

            print(f'is_admin_base: {message.from_user.id in admins_id}')
            return message.from_user.id in admins_id

        print(f'is_admin_cache: {cache_admins[str(message.from_user.id)] == "1"}')
        return cache_admins[str(message.from_user.id)] == '1'


class IsSuperAdmin(BaseFilter):
    keyword = 'is_super_admin'

    async def __call__(self, message: Message, session: AsyncSession, cache: CacheAccess) -> bool:
        print(f'is_super_admin: {message.from_user.id in config.tg_bot.super_admin}')
        return message.from_user.id in config.tg_bot.super_admin
