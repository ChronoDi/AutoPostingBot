from aiogram import Router, F
from aiogram.filters import StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.keyboards.pagination import get_refresh_back_remove_keyboard
from tg_bot.states.groups import FSMGroups
from tg_bot.states.main_menu import FSMMainMenu
from tg_bot.utils.cache.cache_access import CacheAccess
from tg_bot.utils.paginator import slice_dict
from tg_bot.utils.process_group import get_group_dict

router: Router = Router()


@router.callback_query(F.data == 'back', or_f(StateFilter(FSMGroups.view_current_group),
                                              StateFilter(FSMGroups.view_groups_to_remove)))
@router.callback_query(F.data == 'groups', StateFilter(FSMMainMenu.main_menu))
async def get_mailing(callback: CallbackQuery, session: AsyncSession,
                    lexicon: TranslatorRunner, state: FSMContext, cache: CacheAccess):
    await state.clear()
    groups_dict = await get_group_dict(session, cache)
    result_dict, num_pages = slice_dict(groups_dict, num_elements=6)
    await state.update_data(result_dict=result_dict, num_pages=num_pages, current_page=0)
    keyboard = await get_refresh_back_remove_keyboard(result_dict['0'], lexicon)

    await callback.message.edit_text(text=lexicon.select.group(), reply_markup=keyboard)

    await state.set_state(FSMGroups.view_groups)
