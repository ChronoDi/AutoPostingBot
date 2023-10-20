from asyncio import sleep

from aiogram import Router, F, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import ChatMemberUpdatedFilter, JOIN_TRANSITION, LEAVE_TRANSITION
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.utils.Inform_admins import inform_admins
from tg_bot.utils.cache.cache_access import CacheAccess
from tg_bot.utils.cache.literals import cache_names
from tg_bot.utils.cache_ttl import cache_ttl
from tg_bot.utils.database.group import edit_group
from tg_bot.utils.exceptions import MailingToChatExist
from tg_bot.utils.process_group import process_add_group, process_inactive_group

router: Router = Router()


@router.my_chat_member(
    ChatMemberUpdatedFilter(
        member_status_changed=JOIN_TRANSITION
    )
)
async def bot_added_to_group(event: types.ChatMemberUpdated,
                             session: AsyncSession, cache: CacheAccess):
    await sleep(1.0)
    if event.chat.id not in cache_ttl.keys():
        await process_add_group(session, event.chat.id, event.chat.type, event.chat.title)
        await cache.add_to_dict(cache_names.GROUPS, str(event.chat.id), event.chat.title)


@router.my_chat_member(
    ChatMemberUpdatedFilter(
        member_status_changed=LEAVE_TRANSITION
    )
)
async def bot_remove_from_group(event: types.ChatMemberUpdated, session: AsyncSession, cache: CacheAccess):
    try:
        await process_inactive_group(session, event.chat.id)
    except MailingToChatExist as e:
        text: str = f'Бот был исключен из группы {e.message}, хотя туда существует рассылка.'
        await inform_admins(session=session, text=text)
    except TelegramBadRequest:
        pass
    finally:
        await cache.remove_from_dict(cache_names.GROUPS, str(event.chat.id))


@router.message(F.migrate_to_chat_id)
async def group_to_supergroup_migration(message: types.Message, session: AsyncSession):
    await edit_group(session, old_tg_id=message.chat.id,
                     new_tg_int=message.migrate_to_chat_id, new_type='supergroup')
    cache_ttl[message.migrate_to_chat_id] = True