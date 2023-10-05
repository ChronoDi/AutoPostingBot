from asyncio import sleep

from aiogram import Router, Bot, F, types
from aiogram.filters import ChatMemberUpdatedFilter, JOIN_TRANSITION, LEAVE_TRANSITION
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.utils.cache.cache_access import CacheAccess
from tg_bot.utils.cache.literals import cache_names
from tg_bot.utils.cache_ttl import cache_ttl
from tg_bot.utils.database.group import add_group, remove_group, edit_group

router: Router = Router()


@router.my_chat_member(
    ChatMemberUpdatedFilter(
        member_status_changed=JOIN_TRANSITION
    )
)
async def bot_added_to_group(event: types.ChatMemberUpdated, bot: Bot,
                             session: AsyncSession, cache: CacheAccess):
    await sleep(1.0)
    if event.chat.id not in cache_ttl.keys():
        await add_group(session, event.chat.id, event.chat.type, event.chat.title)
        await bot.send_message(110039731, f'Я В группе - {event.chat.title}')
        await cache.add_to_dict(cache_names.GROUPS, str(event.chat.id), event.chat.title)

@router.my_chat_member(
    ChatMemberUpdatedFilter(
        member_status_changed=LEAVE_TRANSITION
    )
)
async def bot_remove_from_group(event: types.ChatMemberUpdated, bot: Bot, session: AsyncSession, cache: CacheAccess):
    await remove_group(session, event.chat.id)
    await bot.send_message(110039731, f'Я ВЫШЕЛ из группы - {event.chat.title}')
    await cache.remove_from_dict(cache_names.GROUPS, str(event.chat.id))


@router.message(F.migrate_to_chat_id)
async def group_to_supergroup_migration(message: types.Message, bot: Bot, session: AsyncSession):
    await edit_group(session, old_tg_id=message.chat.id,
                     new_tg_int=message.migrate_to_chat_id, new_type='supergroup')
    await bot.send_message(110039731, f'Группа - {message.chat.title} сменила тип на supergroup и id на {message.migrate_to_chat_id}')
    cache_ttl[message.migrate_to_chat_id] = True