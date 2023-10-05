from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.keyboards.pagination import get_add_back_remove_keyboard, get_back_scroll_keyboard, get_back_keyboad
from tg_bot.states.mailing import FSMMailing
from tg_bot.utils.exceptions import PostExist
from tg_bot.utils.paginator import slice_dict, get_current_page
from tg_bot.utils.process_mailing import add_post_to_mailing, get_posts_dict, change_mailing_orders
from tg_bot.utils.process_posts import get_post_groups_dict, get_posts_by_group_dict

router: Router = Router()


@router.callback_query(F.data == 'posts', StateFilter(FSMMailing.view_mailing_menu))
@router.callback_query(F.data == 'back', or_f(StateFilter(FSMMailing.view_post_groups),
                                              StateFilter(FSMMailing.remove_post)))
async def process_add_post(callback: CallbackQuery, lexicon: TranslatorRunner,
                            state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    mailing_id = int(data['mailing_id'])
    post_dict = await get_posts_dict(session, mailing_id)
    result_dict, num_pages = slice_dict(post_dict, num_elements=18)
    await state.update_data(result_dict=result_dict, num_pages=num_pages, current_page=0)
    keyboard = await get_add_back_remove_keyboard(lexicon=lexicon, callback_names=result_dict['0'], width=3)
    await callback.message.edit_text(text=lexicon.posts.list(), reply_markup=keyboard)
    await state.set_state(FSMMailing.add_post)


@router.callback_query(or_f(F.data.contains('up'), F.data.contains('down')),
                       StateFilter(FSMMailing.add_post))
async def process_post_order(callback: CallbackQuery, lexicon: TranslatorRunner,
                            state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    mailing_id = int(data['mailing_id'])
    post_id = int(callback.data.split('_')[0])
    is_increase: bool = True if 'up' in callback.data else False
    await change_mailing_orders(session, mailing_id, post_id, is_increase)
    current_page = str(data['current_page'])
    post_dict = await get_posts_dict(session, mailing_id)
    result_dict, num_pages = slice_dict(post_dict, num_elements=18)
    await state.update_data(result_dict=result_dict, num_pages=num_pages)
    keyboard = await get_add_back_remove_keyboard(lexicon=lexicon, callback_names=result_dict[current_page], width=3)

    try:
        await callback.message.edit_text(text=lexicon.posts.list(), reply_markup=keyboard)
    except TelegramBadRequest:
        await callback.answer()


@router.callback_query(F.data == 'add', StateFilter(FSMMailing.add_post))
@router.callback_query(F.data == 'back', or_f(StateFilter(FSMMailing.view_posts),
                                              StateFilter(FSMMailing.post_added)))
async def view_posts_group(callback: CallbackQuery, lexicon: TranslatorRunner,
                            state: FSMContext, session: AsyncSession):
    post_groups_dict = await get_post_groups_dict(session)
    result_dict, num_pages = slice_dict(post_groups_dict, num_elements=6)
    await state.update_data(result_dict=result_dict, num_pages=num_pages, current_page=0)
    keyboard = await get_back_scroll_keyboard(result_dict['0'], lexicon)
    await state.set_state(FSMMailing.view_post_groups)

    await callback.message.edit_text(text=lexicon.view.posts.group(), reply_markup=keyboard)


@router.callback_query(or_f(F.data == 'previous', F.data == 'next'), StateFilter(FSMMailing.add_post))
async def process_paginator_groups(callback: CallbackQuery, state: FSMContext, lexicon: TranslatorRunner):
    is_next = True if callback.data == 'next' else False
    posts_group: dict[str: str] = await get_current_page(state, is_next)
    keyboard = await get_add_back_remove_keyboard(posts_group, lexicon, width=3)

    try:
      await callback.message.edit_text(text=lexicon.posts.list(), reply_markup=keyboard)
    except TelegramBadRequest:
      await callback.answer()


@router.callback_query(StateFilter(FSMMailing.view_post_groups))
async def process_get_posts_by_group(callback: CallbackQuery, state: FSMContext,
                                     lexicon: TranslatorRunner, session:AsyncSession):
   group = callback.data
   special_symbol = None
   posts_dict: dict[str, str] = await get_posts_by_group_dict(session, group)
   result_dict, num_pages = slice_dict(posts_dict, num_elements=7)
   await state.update_data(result_dict=result_dict, num_pages=num_pages, current_page=0, group=callback.data)
   keyboard = await get_back_scroll_keyboard(result_dict['0'], lexicon, special_symbol=special_symbol)
   await callback.message.edit_text(text=lexicon.post.to.mailing(), reply_markup=keyboard)
   await state.set_state(FSMMailing.view_posts)


@router.callback_query(or_f(F.data == 'previous', F.data == 'next'), StateFilter(FSMMailing.view_posts))
async def process_paginator_groups(callback: CallbackQuery, state: FSMContext, lexicon: TranslatorRunner):
    is_next = True if callback.data == 'next' else False
    posts_group: dict[str: str] = await get_current_page(state, is_next)
    keyboard = await get_back_scroll_keyboard(posts_group, lexicon)

    try:
      await callback.message.edit_text(text=lexicon.post.to.mailing(), reply_markup=keyboard)
    except TelegramBadRequest:
      await callback.answer()


@router.callback_query(StateFilter(FSMMailing.view_posts))
async def process_select_post(callback: CallbackQuery, state: FSMContext,
                                     lexicon: TranslatorRunner, session:AsyncSession):
    data = await state.get_data()
    mailing_id = int(data['mailing_id'])
    group_id = callback.data
    keyboard = await get_back_keyboad(lexicon)

    try:
        mailing_name, post_name = await add_post_to_mailing(session, mailing_id, group_id)
        await callback.message.edit_text(text=lexicon.post.added(name=post_name), reply_markup=keyboard)
        await state.set_state(FSMMailing.post_added)
    except PostExist:
        await callback.answer(text=lexicon.post.exist())

