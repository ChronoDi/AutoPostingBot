from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.utils.cache.cache_access import CacheAccess
from tg_bot.utils.process_user import register_user

router: Router = Router()


@router.message(CommandStart())
async def process_start_command(message: Message, state: FSMContext,
                                lexicon: TranslatorRunner, session: AsyncSession, cache: CacheAccess):
    await state.clear()
    await register_user(message, session, cache)
    await message.answer(text=lexicon.start(username=message.from_user.first_name))

