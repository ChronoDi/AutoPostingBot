from typing import Union

from aiogram import Router, F
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from fluentogram import TranslatorRunner

from tg_bot.filters.admins import IsAdmin
from tg_bot.keyboards.main_menu import get_main_menu_keyboard
from tg_bot.states.mailing import FSMMailing
from tg_bot.states.main_menu import FSMMainMenu
from tg_bot.states.posts import FSMPosts

router: Router = Router()
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


@router.callback_query(F.data == 'back', or_f(StateFilter(FSMPosts.view_post_groups),
                                              StateFilter(FSMMailing.view_mailing)))
@router.message(Command(commands='menu'))
async def show_main_menu(event: Union[Message, CallbackQuery],
                    lexicon: TranslatorRunner, state: FSMContext):
    keyboard = await get_main_menu_keyboard(lexicon)

    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text=lexicon.main.menu(), reply_markup=keyboard)
    else:
        await event.answer(text=lexicon.main.menu(), reply_markup=keyboard)

    await state.set_state(FSMMainMenu.main_menu)