import datetime

from aiogram.types import InlineKeyboardMarkup
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.keyboards.fabric import get_inline_keyboards
from tg_bot.utils.process_mailing import get_group_name_mailing, get_date


async def get_to_mailing_keyboard(lexicon: TranslatorRunner) -> InlineKeyboardMarkup:
    return get_inline_keyboards(width=1, callback_names={'back' : lexicon.to.mailing()})


async def get_mailing_menu(lexicon: TranslatorRunner, session: AsyncSession,  mailing_id: int) -> InlineKeyboardMarkup:
    current_group_name = await get_group_name_mailing(session, mailing_id)
    date: datetime = await get_date(session, mailing_id)

    callback_names = {'posts' : lexicon.control.posts(),
                      'date' : lexicon.change.date(date=date, time=str(date.time())),
                      'group' : lexicon.change.group(name=current_group_name)}
    last_buttons = {'back' : lexicon.back()}

    return get_inline_keyboards(width=1, callback_names=callback_names, first_last_buttons=last_buttons)