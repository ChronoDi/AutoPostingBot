from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from fluentogram import TranslatorRunner

from tg_bot.keyboards.pagination import get_add_back_remove_keyboard
from tg_bot.states.mailing import FSMMailing
from tg_bot.utils.paginator import get_current_page_from_dict

router: Router = Router()

@router.callback_query(or_f(F.data == 'previous', F.data == 'next'), StateFilter(FSMMailing.view_mailing))
async def process_paginator_mailing(callback: CallbackQuery, state: FSMContext, lexicon: TranslatorRunner):
   is_next = True if callback.data == 'next' else False
   posts_group: dict[str: str] = await get_current_page_from_dict(state, is_next)
   keyboard = await get_add_back_remove_keyboard(posts_group, lexicon)

   try:
      await callback.message.edit_text(text=lexicon.select.mailing(), reply_markup=keyboard)
   except TelegramBadRequest:
      await callback.answer()