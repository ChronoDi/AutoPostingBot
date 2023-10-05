from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from fluentogram import TranslatorRunner

router: Router = Router()


@router.message(CommandStart())
async def process_start_command(message: Message, state: FSMContext, lexicon: TranslatorRunner):
    await state.clear()
    await message.answer(text=lexicon.start(username=message.from_user.first_name))

