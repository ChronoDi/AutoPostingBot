from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError
from sqlalchemy.ext.asyncio import async_sessionmaker

from tg_bot.database.models import Group
from tg_bot.utils.cache.cache_access import CacheAccess
from tg_bot.utils.cache.literals import cache_names
from tg_bot.utils.database.group import get_all_groups, remove_group


async def init_groups(cache: CacheAccess, session_pool: async_sessionmaker, bot: Bot):
    async with session_pool() as session:
        groups: list[Group] = await get_all_groups(session)

        for group in groups:
            try:
                chat = await bot.get_chat(group.tg_id)
                await cache.add_to_dict(cache_names.GROUPS, str(chat.id), chat.title)
            except TelegramForbiddenError:
                await remove_group(session, group.tg_id)
