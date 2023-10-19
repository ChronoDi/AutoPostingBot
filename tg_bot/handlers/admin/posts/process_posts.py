from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.keyboards.pagination import get_add_back_keyboard, get_back_remove_keyboard, get_back_keyboad, \
   get_back_scroll_keyboard
from tg_bot.states.posts import FSMPosts
from tg_bot.utils.paginator import get_current_page_from_dict, slice_dict
from tg_bot.utils.process_posts import get_posts_by_group_dict, remove_post, load_post

router: Router = Router()

@router.callback_query(or_f(F.data == 'previous', F.data == 'next'), StateFilter(FSMPosts.view_post_groups))
async def process_paginator_groups(callback: CallbackQuery, state: FSMContext, lexicon: TranslatorRunner):
   is_next = True if callback.data == 'next' else False
   posts_group: dict[str: str] = await get_current_page_from_dict(state, is_next)
   keyboard = await get_add_back_keyboard(posts_group, lexicon)

   try:
      await callback.message.edit_text(text=lexicon.view.posts.group(), reply_markup=keyboard)
   except TelegramBadRequest:
      await callback.answer()


@router.callback_query(StateFilter(FSMPosts.view_post_groups))
async def process_get_posts_by_group(callback: CallbackQuery, state: FSMContext,
                                     lexicon: TranslatorRunner, session:AsyncSession):
   group = callback.data
   special_symbol = None
   await state.set_state(FSMPosts.view_post)
   posts_dict: dict[str, str] = await get_posts_by_group_dict(session, group)
   result_dict, num_pages = slice_dict(posts_dict, num_elements=7)
   await state.update_data(result_dict=result_dict, num_pages=num_pages, current_page=0, group=callback.data)
   keyboard = await get_back_remove_keyboard(result_dict['0'], lexicon, special_symbol=special_symbol)
   await callback.message.edit_text(text=lexicon.select.post(), reply_markup=keyboard)


@router.callback_query(F.data == 'remove',  StateFilter(FSMPosts.view_post))
async def process_remove_post(callback: CallbackQuery, state: FSMContext,
                                     lexicon: TranslatorRunner, session:AsyncSession):
   data = await state.get_data()
   group = data['group']
   posts_dict: dict[str, str] = await get_posts_by_group_dict(session, group)
   result_dict, num_pages = slice_dict(posts_dict, num_elements=7)
   await state.update_data(result_dict=result_dict, num_pages=num_pages, current_page=0, group=callback.data)
   keyboard = await get_back_scroll_keyboard(result_dict['0'], lexicon, special_symbol='❌')
   await callback.message.edit_text(text=lexicon.select.post(), reply_markup=keyboard)
   await state.set_state(FSMPosts.remove_post)

@router.callback_query(or_f(F.data == 'previous', F.data == 'next'),
                       or_f(StateFilter(FSMPosts.view_post), StateFilter(FSMPosts.remove_post)))
async def process_paginator_posts(callback: CallbackQuery, state: FSMContext, lexicon: TranslatorRunner):
   is_next = True if callback.data == 'next' else False
   current_state = await state.get_state()
   special_symbol = '❌' if current_state == FSMPosts.remove_post else None
   posts: dict[str: str] = await get_current_page_from_dict(state, is_next)
   keyboard = await get_back_scroll_keyboard(posts, lexicon, special_symbol)

   try:
      await callback.message.edit_text(text=lexicon.select.post(), reply_markup=keyboard)
   except TelegramBadRequest:
      await callback.answer()


@router.callback_query(StateFilter(FSMPosts.remove_post))
async def process_remove_post(callback: CallbackQuery, lexicon: TranslatorRunner,
                              session: AsyncSession, state: FSMContext):
   await remove_post(session=session, group_id=callback.data)

   data = await state.get_data()
   result_dict: dict[str, dict[str, str]] = data['result_dict']
   current_page = data['current_page']
   result_dict[str(current_page)].pop(callback.data)
   special_symbol = '❌'
   keyboard = await get_back_scroll_keyboard(result_dict[str(current_page)], lexicon, special_symbol)

   await callback.message.edit_text(text=lexicon.select.post(), reply_markup=keyboard)
   await state.update_data(result_dict=result_dict)


@router.callback_query(StateFilter(FSMPosts.view_post))
async def view_post(callback: CallbackQuery, lexicon: TranslatorRunner,
                    session: AsyncSession, state: FSMContext, bot: Bot):
   group_id = callback.data
   file_list, text = await load_post(session=session, media_id=group_id)
   keyboard = await get_back_keyboad(lexicon)

   if file_list:
      await bot.send_media_group(callback.message.chat.id, media=file_list)
      await callback.message.answer(text = lexicon.back.to.post(), reply_markup=keyboard)
   else:
      await callback.message.edit_text(text=text, reply_markup=keyboard)

   await state.set_state(FSMPosts.back_to_posts)


@router.callback_query(F.data == 'back', StateFilter(FSMPosts.back_to_posts))
async def back_to_posts(callback: CallbackQuery, state: FSMContext, lexicon: TranslatorRunner):
   data = await state.get_data()
   result_dict: dict[str, dict[str, str]] = data['result_dict']
   current_page = data['current_page']
   keyboard = await get_back_remove_keyboard(result_dict[str(current_page)], lexicon)

   await callback.message.edit_text(text=lexicon.select.post(), reply_markup=keyboard)
   await state.set_state(FSMPosts.view_post)