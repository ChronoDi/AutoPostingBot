from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.keyboards.pagination import get_back_scroll_keyboard
from tg_bot.states.groups import FSMGroups
from tg_bot.utils.cache.cache_access import CacheAccess
from tg_bot.utils.paginator import slice_dict, get_current_page_from_dict
from tg_bot.utils.process_group import get_group_dict
from tg_bot.utils.process_mailing import get_mailing_by_group

router: Router = Router()


@router.callback_query(F.data == 'remove', StateFilter(FSMGroups.view_groups))
async def process_remove_callback(callback: CallbackQuery, state: FSMContext, lexicon: TranslatorRunner,
                                 session: AsyncSession, cache: CacheAccess):
    await state.clear()
    groups_dict = await get_group_dict(session, cache)
    result_dict, num_pages = slice_dict(groups_dict, num_elements=6)
    await state.update_data(result_dict=result_dict, num_pages=num_pages, current_page=0)
    keyboard = await get_back_scroll_keyboard(result_dict['0'], lexicon, special_symbol='❌')

    await callback.message.edit_text(text=lexicon.select.group(), reply_markup=keyboard)

    await state.set_state(FSMGroups.view_groups_to_remove)


@router.callback_query(or_f(F.data == 'previous', F.data == 'next'), StateFilter(FSMGroups.view_groups_to_remove))
async def process_paginator_groups(callback: CallbackQuery, state: FSMContext, lexicon: TranslatorRunner):
   is_next = True if callback.data == 'next' else False
   groups_dict: dict[str: str] = await get_current_page_from_dict(state, is_next)
   keyboard = await get_back_scroll_keyboard(groups_dict, lexicon, special_symbol='❌')

   try:
      await callback.message.edit_text(text=lexicon.select.group(), reply_markup=keyboard)
   except TelegramBadRequest:
      await callback.answer()


@router.callback_query(StateFilter(FSMGroups.view_groups_to_remove))
async def process_remove(callback: CallbackQuery, state: FSMContext, lexicon: TranslatorRunner,
                                 session: AsyncSession, bot: Bot):
    data = await state.get_data()
    result_dict = data['result_dict']
    current_page = str(data['current_page'])
    mailing_exist: bool = await get_mailing_by_group(session, int(callback.data))

    if not mailing_exist:
        await bot.get_chat(int(callback.data))
        await bot.leave_chat(int(callback.data))
        result_dict[current_page].pop(callback.data)
        await state.update_data(result_dict=result_dict)
        keyboard = await get_back_scroll_keyboard(result_dict[current_page], lexicon, special_symbol='❌')
        await callback.message.edit_text(text=lexicon.select.group(), reply_markup=keyboard)
    else:
        await callback.answer(text=lexicon.group.inmailing())

