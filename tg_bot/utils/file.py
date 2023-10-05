import os
from aiogram import Bot
from aiogram.enums import ContentType
from aiogram.types import Message, TelegramObject

from tg_bot.config_data import config


async def download_file(bot: Bot, file_id: str, name: str, folder: str):
    path = f'{config.paths.media}/{folder}'
    file = await bot.get_file(file_id)
    file_path = await bot.download_file(file.file_path)
    new_file_path = f'{path}/{name}'

    os.makedirs(path, exist_ok=True)

    with open(new_file_path, 'wb') as f:
        f.write(file_path.getvalue())

    return new_file_path

def get_file_by_type(message: Message) -> TelegramObject | None:
    file_type = message.content_type

    match file_type:
        case ContentType.VIDEO:
            return message.video
        case ContentType.VOICE:
            return message.voice
        case ContentType.AUDIO:
            return message.audio
        case ContentType.DOCUMENT:
            return message.document
