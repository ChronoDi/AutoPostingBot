# from aiogram import Router, Bot
# from aiogram.filters import Command, StateFilter
# from aiogram.fsm.context import FSMContext
# from aiogram.types import Message, CallbackQuery
# from sqlalchemy import select, distinct
# from sqlalchemy.ext.asyncio import AsyncSession
#
# from tg_bot.database.models import Post
# from tg_bot.keyboards import get_groups_keyboard
# from tg_bot.states.test import TestState
# from tg_bot.utils.cache.cache_access import CacheAccess
# from tg_bot.utils.process_posts import load_post
#
# router: Router = Router()
#
#
# @router.message(Command(commands='send'))
# async def take_group(message: Message, cache: CacheAccess, state: FSMContext, session: AsyncSession):
#     await state.clear()
#     keyboard = await get_groups_keyboard(session=session, cache=cache)
#     await message.answer(text='Выберете группу для отправки', reply_markup=keyboard)
#     await state.set_state(TestState.take_post)
#
#
# @router.callback_query(StateFilter(TestState.take_post))
# async def take_post(callback: CallbackQuery, state: FSMContext):
#     await state.update_data(group_id=int(callback.data))
#     await callback.message.answer(text='Введите id поста')
#     await state.set_state(TestState.show_save_post)
#
#
# @router.message(StateFilter(TestState.show_save_post))
# async def show_post(message: Message, session: AsyncSession, state: FSMContext, bot: Bot):
#     data = await state.get_data()
#     group_id = data['group_id']
#     file_list, text = await load_post(session=session, media_id=message.text)
#
#     if file_list:
#         await bot.send_media_group(group_id, media=file_list)
#     else:
#         await bot.send_message(group_id, text=text)
#
#
# @router.message(Command(commands='test'))
# async def take_unique_group_names(message: Message, session: AsyncSession):
#     result = await session.execute(select(distinct(Post.group)))
#     unique_values = [row[0] for row in result]
#
#     for value in unique_values:
#         print(f'**************\n{value}')
