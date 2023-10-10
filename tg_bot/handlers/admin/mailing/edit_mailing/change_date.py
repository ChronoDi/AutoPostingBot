from datetime import datetime

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.keyboards.pagination import get_back_keyboad
from tg_bot.states.mailing import FSMMailing
from tg_bot.utils.process_mailing import change_date
from tkq import db_source

# from tg_bot.utils.taskiq import TaskiqController

router: Router = Router()


@router.callback_query(F.data == 'next', StateFilter(FSMMailing.edit_time))
async def process_edit_time(callback: CallbackQuery, lexicon: TranslatorRunner,
                            state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    year = int(data['year'])
    day = int(data['day'])
    month = int(data['month'])
    hour = int(data['hour'])
    minute = int(data['minute'])
    mailing_id = int(data['mailing_id'])

    date = datetime(year, month, day, hour, minute)
    await change_date(session, mailing_id, date)
    await db_source.reschedule_task(mailing_id, new_time=date)
    keyboard = await get_back_keyboad(lexicon)
    await callback.message.edit_text(text=lexicon.date.edited(), reply_markup=keyboard)
    await state.set_state(FSMMailing.time_edited)

