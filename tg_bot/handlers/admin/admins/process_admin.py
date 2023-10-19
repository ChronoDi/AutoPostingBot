from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.database.models import User, Role
from tg_bot.keyboards.pagination import get_add_scroll_keyboard, get_back_keyboad, get_only_remove_back_keyboad
from tg_bot.states.admins import FSMAdmins
from tg_bot.utils.cache.cache_access import CacheAccess
from tg_bot.utils.paginator import get_current_page_from_dict
from tg_bot.utils.process_user import get_user, change_user_role

router: Router = Router()


@router.callback_query(or_f(F.data == 'previous', F.data == 'next'), StateFilter(FSMAdmins.view_admins))
async def process_paginator_groups(callback: CallbackQuery, state: FSMContext, lexicon: TranslatorRunner):
   is_next = True if callback.data == 'next' else False
   posts_group: dict[str: str] = await get_current_page_from_dict(state, is_next)
   keyboard = await get_add_scroll_keyboard(posts_group, lexicon)

   try:
      await callback.message.edit_text(text=lexicon.view.admins(), reply_markup=keyboard)
   except TelegramBadRequest:
      await callback.answer()


@router.callback_query(F.data != 'add', StateFilter(FSMAdmins.view_admins))
async def view_admin_info(callback: CallbackQuery, state: FSMContext,
                          lexicon: TranslatorRunner, session: AsyncSession):
   await state.update_data(admin_id=callback.data)
   user: User = await get_user(session, int(callback.data))

   if user:
        keyboard = await get_back_keyboad(lexicon) if user.role == Role.SUPER_ADMIN else\
           await get_only_remove_back_keyboad(lexicon)
        await state.update_data(tg_id=user.tg_id)
        await callback.message.edit_text(text = lexicon.user.info(first_name=str(user.first_name),
                                                                second_name=str(user.second_name),
                                                                username=str(user.user_name),
                                                                role=str(user.role),
                                                                date=user.created_at),
                                       reply_markup=keyboard)
        await state.set_state(FSMAdmins.view_current_admin)
   else:
        keyboard = await get_back_keyboad(lexicon)
        await callback.message.edit_text(text=lexicon.user.notfound(), reply_markup=keyboard)
        await state.set_state(FSMAdmins.view_current_admin)


@router.callback_query(F.data == 'remove', StateFilter(FSMAdmins.view_current_admin))
async def remove_admin(callback: CallbackQuery, state: FSMContext,
                          lexicon: TranslatorRunner, session: AsyncSession, cache: CacheAccess):
    data = await state.get_data()
    tg_id = int(data['tg_id'])
    await change_user_role(session, cache, tg_id, role=Role.USER)
    keyboard = await get_back_keyboad(lexicon)
    await callback.message.edit_text(text=lexicon.admin.removed(), reply_markup=keyboard)
    await state.set_state(FSMAdmins.role_changed)




