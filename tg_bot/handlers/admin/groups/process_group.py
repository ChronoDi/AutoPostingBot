from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import or_f, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.database.models import Group
from tg_bot.keyboards.pagination import get_refresh_back_remove_keyboard, get_back_keyboad
from tg_bot.states.groups import FSMGroups
from tg_bot.utils.cache.cache_access import CacheAccess
from tg_bot.utils.cache.groups import init_groups
from tg_bot.utils.paginator import get_current_page_from_dict, slice_dict
from tg_bot.utils.process_group import get_group_dict, process_get_group

router: Router = Router()


@router.callback_query(or_f(F.data == 'previous', F.data == 'next'), StateFilter(FSMGroups.view_groups))
async def process_paginator_groups(callback: CallbackQuery, state: FSMContext, lexicon: TranslatorRunner):
   is_next = True if callback.data == 'next' else False
   groups_dict: dict[str: str] = await get_current_page_from_dict(state, is_next)
   keyboard = await get_refresh_back_remove_keyboard(groups_dict, lexicon)

   try:
      await callback.message.edit_text(text=lexicon.select.group(), reply_markup=keyboard)
   except TelegramBadRequest:
      await callback.answer()


@router.callback_query(F.data == 'refresh', StateFilter(FSMGroups.view_groups))
async def process_refresh_groups(callback: CallbackQuery, state: FSMContext, lexicon: TranslatorRunner,
                                 session: AsyncSession, cache: CacheAccess, bot: Bot):
   await init_groups(session=session, cache=cache, bot=bot)
   groups_dict = await get_group_dict(session, cache)
   result_dict, num_pages = slice_dict(groups_dict, num_elements=6)
   await state.update_data(result_dict=result_dict, num_pages=num_pages, current_page=0)
   keyboard = await get_refresh_back_remove_keyboard(result_dict['0'], lexicon)

   try:
      await callback.message.edit_text(text=lexicon.select.group(), reply_markup=keyboard)
   except TelegramBadRequest:
      await callback.answer()


@router.callback_query(StateFilter(FSMGroups.view_groups))
async def process_view_group_info(callback: CallbackQuery, state: FSMContext, lexicon: TranslatorRunner,
                                 session: AsyncSession):
   group: Group = await process_get_group(session, int(callback.data))
   text: str = lexicon.group.info(name=group.title,
                                  type=group.type,
                                  tg_id=group.tg_id)
   keyboard = await get_back_keyboad(lexicon)

   await callback.message.edit_text(text=text, reply_markup=keyboard)
   await state.set_state(FSMGroups.view_current_group)
