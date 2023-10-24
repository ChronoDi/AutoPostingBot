from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.database.models import Group
from tg_bot.utils.cache.cache_access import CacheAccess
from tg_bot.utils.cache.literals import cache_names
from tg_bot.utils.database.group import get_all_active_groups, refresh_group
from tg_bot.utils.process_group import process_inactive_group


async def init_groups(cache: CacheAccess, session: AsyncSession, bot: Bot):
    groups: list[Group] = await get_all_active_groups(session)

    for group in groups:
        try:
            chat = await bot.get_chat(group.tg_id)
            await cache.add_to_dict(cache_names.GROUPS, str(chat.id), chat.title)
            await refresh_group(session, group, chat.title)
        except TelegramForbiddenError:
            await process_inactive_group(session, group.tg_id)
