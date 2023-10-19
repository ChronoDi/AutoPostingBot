from aiogram import Router,html
from aiogram.filters import Command
from aiogram.types import Message
from fluentogram import TranslatorRunner


router: Router = Router()


@router.message(Command(commands='id'))
async def process_start_command(message: Message, lexicon: TranslatorRunner):
    await message.answer(text=lexicon.user.id(id=html.code(message.from_user.id)))