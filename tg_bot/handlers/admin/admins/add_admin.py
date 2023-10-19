from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.database.models import User, Role
from tg_bot.keyboards.pagination import get_only_add_back_keyboad, get_back_keyboad
from tg_bot.states.admins import FSMAdmins
from tg_bot.utils.cache.cache_access import CacheAccess
from tg_bot.utils.process_user import get_user_tg_id, change_user_role

router: Router = Router()


@router.callback_query(F.data == 'add', StateFilter(FSMAdmins.view_admins))
async def take_user_info(callback: CallbackQuery, state: FSMContext, lexicon: TranslatorRunner):
    await callback.message.edit_text(text=lexicon.take.user.info())
    await state.set_state(FSMAdmins.take_user_info)


@router.message(F.text.isdigit(), StateFilter(FSMAdmins.take_user_info))
async def search_admin_by_id(message: Message, state: FSMContext, lexicon: TranslatorRunner,
                             session: AsyncSession):
    user: User = await get_user_tg_id(session, int(message.text))

    if user:
        keyboard = await get_only_add_back_keyboad(lexicon)
        await message.answer(text = lexicon.user.info(first_name=str(user.first_name),
                                                                second_name=str(user.second_name),
                                                                username=str(user.user_name),
                                                                role=str(user.role),
                                                                date=user.created_at),
                                       reply_markup=keyboard)
        await state.update_data(tg_id=message.text)
        await state.set_state(FSMAdmins.confirmation_add_user)
    else:
        await message.answer(text=f'{lexicon.user.notfound()}\n{lexicon.take.user.info()}')

@router.message(StateFilter(FSMAdmins.take_user_info))
async def process_error_input(message: Message, lexicon: TranslatorRunner):
    await message.answer(text=lexicon.error.input())


@router.callback_query(F.data == 'add', StateFilter(FSMAdmins.confirmation_add_user))
async def add_admin(callback: CallbackQuery, state: FSMContext, lexicon: TranslatorRunner,
                             session: AsyncSession, cache: CacheAccess):
    data = await state.get_data()
    tg_id = int(data['tg_id'])
    await change_user_role(session, cache, tg_id=tg_id, role=Role.ADMIN)
    keyboard = await get_back_keyboad(lexicon)
    await callback.message.edit_text(text=lexicon.user.added(), reply_markup=keyboard)
    await state.set_state(FSMAdmins.role_changed)
