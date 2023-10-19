from aiogram import Router, F
from aiogram.filters import StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.keyboards.pagination import get_add_back_remove_keyboard
from tg_bot.states.mailing import FSMMailing
from tg_bot.states.main_menu import FSMMainMenu
from tg_bot.utils.process_mailing import get_mailing_dict
from tg_bot.utils.paginator import slice_dict

router: Router = Router()

@router.callback_query(F.data == 'back', or_f(StateFilter(FSMMailing.create_mailing),
                                              StateFilter(FSMMailing.view_mailing_to_remove),
                                              StateFilter(FSMMailing.view_mailing_menu),
                                              StateFilter(FSMMailing.error_state)))
@router.callback_query(F.data == 'mailing', StateFilter(FSMMainMenu.main_menu))
async def get_mailing(callback: CallbackQuery, session: AsyncSession,
                    lexicon: TranslatorRunner, state: FSMContext):
    await state.clear()
    mailing_dict = await get_mailing_dict(session)
    result_dict, num_pages = slice_dict(mailing_dict, num_elements=6)
    await state.update_data(result_dict=result_dict, num_pages=num_pages, current_page=0)
    keyboard = await get_add_back_remove_keyboard(result_dict['0'], lexicon)

    await callback.message.edit_text(text=lexicon.select.mailing(), reply_markup=keyboard)

    await state.set_state(FSMMailing.view_mailing)

