from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.utils.cache.cache_access import CacheAccess
from tg_bot.utils.cache.literals import cache_names
from tg_bot.utils.database.group import get_all_groups


async def get_group_dict(session: AsyncSession, cache: CacheAccess) -> dict[str, str]:
    result = await cache.check_entity(cache_names.GROUPS)

    if result:
        group_dict = await cache.get_dict(cache_names.GROUPS)
        return group_dict

    groups = await get_all_groups(session)
    group_dict: dict[str, str] = {}

    for group in groups:
        group_dict.update({str(group.tg_id) : group.title})

    return group_dict
