from aiogram import Router, F
from aiogram.filters import StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.keyboards.mailing import get_mailing_menu
from tg_bot.keyboards.pagination import get_back_keyboad
from tg_bot.states.mailing import FSMMailing

router: Router = Router()

@router.callback_query(StateFilter(FSMMailing.view_mailing))
@router.callback_query(F.data == 'back', or_f(StateFilter(FSMMailing.group_changed),
                                              StateFilter(FSMMailing.time_edited),
                                              StateFilter(FSMMailing.add_post)))
async def process_select_mailing(callback: CallbackQuery, lexicon: TranslatorRunner, state: FSMContext,
                                 session: AsyncSession):
    if callback.data != 'back':
        await state.clear()
        await state.update_data(mailing_id=callback.data)
        mailing_id = int(callback.data)

    else:
        data = await state.get_data()
        mailing_id = int(data['mailing_id'])

    try:
        keyboard = await get_mailing_menu(lexicon, session, mailing_id)
        await callback.message.edit_text(text=lexicon.main.menu(), reply_markup=keyboard)
        await state.set_state(FSMMailing.view_mailing_menu)
    except AttributeError:
        keyboard = await get_back_keyboad(lexicon)
        await callback.message.edit_text(text=lexicon.mailing.notfound(), reply_markup=keyboard)
        await state.set_state(FSMMailing.error_state)



