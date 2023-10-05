from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.keyboards.groups import get_groups_keyboard
from tg_bot.keyboards.pagination import get_back_keyboad
from tg_bot.states.mailing import FSMMailing
from tg_bot.utils.cache.cache_access import CacheAccess
from tg_bot.utils.paginator import slice_dict, get_current_page
from tg_bot.utils.process_group import get_group_dict
from tg_bot.utils.process_mailing import change_group

router: Router = Router()

@router.callback_query(F.data == 'group', StateFilter(FSMMailing.view_mailing_menu))
async def process_edit_group(callback: CallbackQuery, lexicon: TranslatorRunner, state: FSMContext,
                                 session: AsyncSession, cache: CacheAccess):
    group_dict = await get_group_dict(session, cache)
    result_dict, num_pages = slice_dict(group_dict, num_elements=6)
    await state.update_data(result_dict=result_dict, num_pages=num_pages, current_page=0)
    keyboard = await get_groups_keyboard(result_dict['0'])
    await callback.message.edit_text(text=lexicon.select.group(), reply_markup=keyboard)
    await state.set_state(FSMMailing.change_group)


@router.callback_query(or_f(F.data == 'previous', F.data == 'next'), StateFilter(FSMMailing.change_group))
async def process_paginator_groups(callback: CallbackQuery, state: FSMContext, lexicon: TranslatorRunner):
    is_next = True if callback.data == 'next' else False
    posts_group: dict[str: str] = await get_current_page(state, is_next)
    keyboard = await get_groups_keyboard(posts_group)

    try:
      await callback.message.edit_text(text=lexicon.current.group(text=lexicon.select.group(), reply_markup=keyboard))
    except TelegramBadRequest:
      await callback.answer()


@router.callback_query(StateFilter(FSMMailing.change_group))
async def process_change_group(callback: CallbackQuery, state: FSMContext, lexicon: TranslatorRunner, session: AsyncSession):
    data = await state.get_data()
    mailing_id = data['mailing_id']
    await change_group(session, int(mailing_id), int(callback.data))
    current_page = data['current_page']
    group_dict = data['result_dict']
    group_name = group_dict[str(current_page)][callback.data]
    keyboard = await get_back_keyboad(lexicon)
    await callback.message.edit_text(text=lexicon.group.changed(name=group_name), reply_markup=keyboard)
    await state.set_state(FSMMailing.group_changed)

