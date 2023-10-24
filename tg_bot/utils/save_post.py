import logging
from aiogram import Bot
from aiogram.enums import ContentType
from aiogram.types import Message, TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.utils.database.post import add_text_post, add_media_post, creat_new_post
from tg_bot.utils.file import download_file, get_file_by_type
from tg_bot.utils.uudi import take_uuid


def create_media_id(media_group_id: str) -> str:
    if not media_group_id:
        return take_uuid()

    return media_group_id


async def save_text_post(session: AsyncSession, text: str, media_group_id: str, name_post: str):
    await add_text_post(session, text, create_media_id(media_group_id), name_post)
    logging.info(f'The text post {name_post} has been saved')


async def save_file(session: AsyncSession, message: Message, bot: Bot,
                    file: TelegramObject, name: str, folder: str, name_post: str):
    group = 'media' if message.media_group_id else folder
    media_id = create_media_id(message.media_group_id)
    await session.run_sync(creat_new_post, media_id, group=group, name_post=name_post)
    new_file_path = await download_file(bot, file_id=file.file_id, name=name, folder=folder)
    await add_media_post(session, new_file_path, message.caption, media_id=media_id, group=folder)

    return media_id


async def save_media_post(session: AsyncSession, message: Message,  bot: Bot, name_post: str):
    file: TelegramObject = get_file_by_type(message)
    file_attributes = file.mime_type.split('/')
    name = f'{take_uuid()}.{file_attributes[-1]}'

    if  message.content_type == ContentType.DOCUMENT:
        folder = 'document'
    else:
        folder = file_attributes[0]

    media_id = await save_file(session, message, bot, file, name, folder, name_post)
    logging.info(f'The post {name_post} has been saved')

    return media_id


async def save_photo_post(session: AsyncSession, message: Message,  bot: Bot, name_post: str):
    file = message.photo[-1]
    file = await bot.get_file(file.file_id)
    file_ext = file.file_path.split('.')[-1]
    name = f'{take_uuid()}.{file_ext}'
    folder = 'photo'
    media_id = await save_file(session, message, bot, file, name, folder, name_post)
    logging.info(f'The post {name_post} has been saved')

    return media_id


async def save_video_note(session: AsyncSession, message: Message,  bot: Bot, name_post: str):
    file = await bot.get_file(message.video_note.file_id)
    file_ext = file.file_path.split('.')[-1]
    name = f'{take_uuid()}.{file_ext}'
    folder = 'video_note'
    media_id = await save_file(session, message, bot, file, name, folder, name_post)
    logging.info(f'The post {name_post} has been saved')

    return media_id