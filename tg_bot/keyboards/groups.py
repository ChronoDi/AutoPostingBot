from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.keyboards.fabric import get_inline_keyboards
from tg_bot.utils.cache.cache_access import CacheAccess
from tg_bot.utils.process_group import get_group_dict


async def get_groups_keyboard(group_dict: dict[str, str]):
    last_buttons = {'previous' : '<<', 'next': '>>'}

    return get_inline_keyboards(callback_names=group_dict, width=1, first_last_buttons=last_buttons)


