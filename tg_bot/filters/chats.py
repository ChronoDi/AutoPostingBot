from typing import Union

from aiogram.enums import ChatType
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery


class IsPrivateChat(BaseFilter):
    keyword = 'is_private_chat'

    async def __call__(self, event: Union[Message, CallbackQuery]) -> bool:

        if isinstance(event, CallbackQuery):
            print(event.message.chat.type == ChatType.PRIVATE)
            return event.message.chat.type == ChatType.PRIVATE
        else:
            print(f'is_private_chat - {event.chat.type == ChatType.PRIVATE}')
            return event.chat.type == ChatType.PRIVATE