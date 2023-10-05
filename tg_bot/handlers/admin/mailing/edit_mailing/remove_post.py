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
from tg_bot.utils.process_mailing import get_posts_remove_dict, remove_post_from_mailing

router: Router = Router()

@router.callback_query(F.data == 'remove', StateFilter(FSMMailing.add_post))
async def process_remove_post(callback: CallbackQuery, lexicon: TranslatorRunner,
                            state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    mailing_id = int(data['mailing_id'])
    post_dict = await get_posts_remove_dict(session, mailing_id)
    result_dict, num_pages = slice_dict(post_dict, num_elements=6)
    await state.update_data(result_dict=result_dict, num_pages=num_pages, current_page=0)
    keyboard = await get_back_scroll_keyboard(lexicon=lexicon, callback_names=result_dict['0'],
                                              width=1, special_symbol='❌')
    await callback.message.edit_text(text=lexicon.select.post(), reply_markup=keyboard)
    await state.set_state(FSMMailing.remove_post)


@router.callback_query(or_f(F.data == 'previous', F.data == 'next'), StateFilter(FSMMailing.remove_post))
async def process_paginator_posts(callback: CallbackQuery, state: FSMContext, lexicon: TranslatorRunner):
    is_next = True if callback.data == 'next' else False
    posts_group: dict[str: str] = await get_current_page(state, is_next)
    keyboard = await get_back_scroll_keyboard(posts_group, lexicon, width=1, special_symbol='❌')

    try:
      await callback.message.edit_text(text=lexicon.select.post(), reply_markup=keyboard)
    except TelegramBadRequest:
      await callback.answer()


@router.callback_query(StateFilter(FSMMailing.remove_post))
async def remove_post(callback: CallbackQuery, state: FSMContext,
                      lexicon: TranslatorRunner, session: AsyncSession):
    data = await state.get_data()
    mailing_id = int(data['mailing_id'])
    result_dict = data['result_dict']
    current_page = str(data['current_page'])
    await remove_post_from_mailing(session, mailing_id, int(callback.data), result_dict[current_page])
    keyboard = await get_back_scroll_keyboard(result_dict[current_page], lexicon, width=1, special_symbol='❌')
    await callback.message.edit_text(text=lexicon.select.post(), reply_markup=keyboard)

