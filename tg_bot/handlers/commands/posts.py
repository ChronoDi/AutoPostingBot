
from aiogram import Router, F
from aiogram.filters import StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.keyboards.pagination import get_add_back_keyboard
from tg_bot.states.main_menu import FSMMainMenu
from tg_bot.states.posts import FSMPosts
from tg_bot.utils.process_posts import get_post_groups_dict
from tg_bot.utils.paginator import slice_dict

router: Router = Router()


@router.callback_query(F.data == 'post_groups', StateFilter(FSMPosts.take_post))
@router.callback_query(F.data == 'back', or_f(StateFilter(FSMPosts.view_post), StateFilter(FSMPosts.remove_post)))
@router.callback_query(F.data == 'posts', StateFilter(FSMMainMenu.main_menu))
async def get_posts(callback: CallbackQuery, session: AsyncSession,
                    lexicon: TranslatorRunner, state: FSMContext):
    await state.clear()
    post_groups_dict = await get_post_groups_dict(session)
    result_dict, num_pages = slice_dict(post_groups_dict, num_elements=6)
    await state.update_data(result_dict=result_dict, num_pages=num_pages, current_page=0)
    keyboard = await get_add_back_keyboard(result_dict['0'], lexicon)
    await state.set_state(FSMPosts.view_post_groups)

    await callback.message.edit_text(text=lexicon.view.posts.group(), reply_markup=keyboard)




