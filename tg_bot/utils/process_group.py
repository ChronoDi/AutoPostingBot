from typing import Union

from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.database.models import Group, Mailing
from tg_bot.utils.cache.cache_access import CacheAccess
from tg_bot.utils.cache.literals import cache_names
from tg_bot.utils.database.group import get_all_active_groups, get_group_by_tg_id, change_active, add_group
from tg_bot.utils.database.mailing import get_mailing_by_group_id
from tg_bot.utils.exceptions import MailingToChatExist


async def get_group_dict(session: AsyncSession, cache: CacheAccess) -> dict[str, str]:
    result = await cache.check_entity(cache_names.GROUPS)

    if result:
        group_dict = await cache.get_dict(cache_names.GROUPS)
        return group_dict

    groups = await get_all_active_groups(session)
    group_dict: dict[str, str] = {}

    for group in groups:
        group_dict.update({str(group.tg_id) : group.title})

    return group_dict


async def process_add_group(session: AsyncSession, tg_id: int, group_type: str, title: str):
    group: Group = await get_group_by_tg_id(session, tg_id)

    if group:
        await change_active(session, group, is_active=True)
    else:
        await add_group(session, tg_id, group_type, title)


async def process_inactive_group(session: AsyncSession, tg_id: int):
    group: Group = await get_group_by_tg_id(session, tg_id)

    if group:
        await change_active(session, group, is_active=False)
        mailing: list[Mailing] = await get_mailing_by_group_id(session, tg_id)

        if mailing:
            raise MailingToChatExist(group.title)


async def process_active_group(session: AsyncSession, tg_id: int):
    group: Group = await get_group_by_tg_id(session, tg_id)
    await change_active(session, group, is_active=True)



async def process_get_group(session: AsyncSession, tg_id: int) -> Group:
    group: Group = await get_group_by_tg_id(session, tg_id)

    return group


