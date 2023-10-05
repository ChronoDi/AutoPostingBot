from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.keyboards.pagination import get_back_scroll_keyboard
from tg_bot.states.mailing import FSMMailing
from tg_bot.utils.paginator import slice_dict, get_current_page
from tg_bot.utils.process_mailing import get_mailing_dict, process_remove_mailing
from tg_bot.utils.taskiq import TaskiqController

router: Router = Router()


@router.callback_query(F.data == 'remove', StateFilter(FSMMailing.view_mailing))
async def view_mailing_to_remove(callback: CallbackQuery, state: FSMContext,
                                 lexicon: TranslatorRunner, session: AsyncSession):
    await state.clear()
    mailing_dict = await get_mailing_dict(session)
    result_dict, num_pages = slice_dict(mailing_dict, num_elements=6)
    await state.update_data(result_dict=result_dict, num_pages=num_pages, current_page=0)
    keyboard = await get_back_scroll_keyboard(result_dict['0'], lexicon, special_symbol='❌')
    await callback.message.edit_text(text=lexicon.select.mailing(), reply_markup=keyboard)
    await state.set_state(FSMMailing.view_mailing_to_remove)


@router.callback_query(or_f(F.data == 'previous', F.data == 'next'), StateFilter(FSMMailing.view_mailing_to_remove))
async def process_paginator_mailing(callback: CallbackQuery, state: FSMContext, lexicon: TranslatorRunner):
   is_next = True if callback.data == 'next' else False
   mailing_dict: dict[str: str] = await get_current_page(state, is_next)
   keyboard = await get_back_scroll_keyboard(mailing_dict, lexicon, special_symbol='❌')

   try:
      await callback.message.edit_text(text=lexicon.select.mailing(), reply_markup=keyboard)
   except TelegramBadRequest:
      await callback.answer()


@router.callback_query(StateFilter(FSMMailing.view_mailing_to_remove))
async def remove_mailing(callback: CallbackQuery, state: FSMContext,
                         lexicon: TranslatorRunner, session: AsyncSession, taskiq_controller: TaskiqController):
    data = await state.get_data()
    result_dict = data['result_dict']
    current_page = str(data['current_page'])
    await process_remove_mailing(session, int(callback.data), result_dict[current_page])
    await taskiq_controller.remove_mailing(str(callback.data))
    await state.update_data(result_dict=result_dict)
    keyboard = await get_back_scroll_keyboard(result_dict[current_page], lexicon, width=1, special_symbol='❌')
    await callback.message.edit_text(text=lexicon.select.mailing(), reply_markup=keyboard)


