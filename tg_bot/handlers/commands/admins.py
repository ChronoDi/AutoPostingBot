from typing import Union

from aiogram import Router, F
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.filters.admins import IsSuperAdmin
from tg_bot.keyboards.pagination import get_add_scroll_keyboard
from tg_bot.states.admins import FSMAdmins
from tg_bot.utils.paginator import slice_dict
from tg_bot.utils.process_user import get_admins_dict

router: Router = Router()
router.message.filter(IsSuperAdmin())

@router.callback_query(F.data == 'back', or_f(StateFilter(FSMAdmins.view_current_admin),
                                              StateFilter(FSMAdmins.confirmation_add_user),
                                              StateFilter(FSMAdmins.role_changed),
                                              StateFilter(FSMAdmins.view_users)))
@router.message(Command(commands='admins'))
async def show_admins(event: Union[Message, CallbackQuery], lexicon: TranslatorRunner,
                      state: FSMContext, session: AsyncSession):
    await state.clear()
    admins_dict: dict[str, str] = await get_admins_dict(session)
    result_dict, num_pages = slice_dict(admins_dict, num_elements=6)
    await state.update_data(result_dict=result_dict, num_pages=num_pages, current_page=0)
    keyboard = await get_add_scroll_keyboard(result_dict['0'], lexicon)

    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text=lexicon.view.admins(), reply_markup=keyboard)
    else:
        await event.answer(text=lexicon.view.admins(), reply_markup=keyboard)

    await state.set_state(FSMAdmins.view_admins)