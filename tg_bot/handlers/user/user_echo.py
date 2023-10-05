from pprint import pprint

from aiogram import Router
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.utils.save_post import save_text_post

router = Router()

#
# @router.message()
# async def process_message(message: Message, session: AsyncSession ):
#     pprint(message.content_type)
#     await message.answer(lexicon['user_echo'])


