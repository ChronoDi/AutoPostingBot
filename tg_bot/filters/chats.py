from typing import Union

from aiogram.enums import ChatType
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.utils.cache.cache_access import CacheAccess


class IsPrivateChat(BaseFilter):
    keyword = 'is_private_chat'

    async def __call__(self, event: Union[Message, CallbackQuery]) -> bool:

        if isinstance(event, CallbackQuery):
            return event.message.chat.type == ChatType.PRIVATE
        else:
            return event.chat.type == ChatType.PRIVATE
