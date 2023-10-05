import asyncio
from pprint import pprint

from aiogram import Router, F, Bot, types
from aiogram.filters import or_f
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.filters.admins import IsAdmin
from tg_bot.utils.database.post import add_media_post
from tg_bot.utils.file import download_file
from tg_bot.utils.process_posts import load_post
from tg_bot.utils.save_post import save_text_post, save_media_post, save_photo_post, save_video_note

router = Router()
router.message.filter(IsAdmin())

# @router.message(F.photo)
# async def test(message: Message, bot: Bot, session: AsyncSession):
#     media_id = await save_photo_post(session, message, bot)
#
#
# @router.message(F.text)
# async def process_hello_message(message: Message, session: AsyncSession):
#     await save_text_post(session, message.text, message.media_group_id)
#
#
# @router.message(or_f(F.video, F.voice, F.document, F.audio))
# async def process_video_message(message: Message, session: AsyncSession, bot: Bot):
#     media_id = await save_media_post(session, message, bot)
#
#
# @router.message(F.video_note)
# async def process_none(message: Message, session: AsyncSession, bot: Bot):
#     await save_video_note(session, message, bot)


# @router.message()
# async def get_post(message: Message, session: AsyncSession, bot: Bot):
#     file_list, text = await load_post(session=session, group_id=message.text)
#
#     if file_list:
#         await bot.send_media_group(message.chat.id, media=file_list)
#     else:
#         await bot.send_message(message.chat.id, text=text)

