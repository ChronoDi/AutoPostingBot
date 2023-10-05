from aiogram import Router, F, Bot
from aiogram.filters import StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.keyboards.pagination import get_back_to_post_groups_keyboard
from tg_bot.states.posts import FSMPosts
from tg_bot.utils.cache_ttl import cache_ttl
from tg_bot.utils.save_post import save_photo_post, save_text_post, save_media_post, save_video_note

router: Router = Router()

@router.callback_query(F.data == 'add', StateFilter(FSMPosts.view_post_groups))
async def take_post_name(callback: CallbackQuery, state: FSMContext, lexicon: TranslatorRunner):
    await callback.message.edit_text(text=lexicon.take.name.post())
    await state.set_state(FSMPosts.take_name_post)


@router.message(F.text, StateFilter(FSMPosts.take_name_post))
async def take_post(message: Message, state: FSMContext, lexicon: TranslatorRunner):
    await state.update_data(name_post=message.text)
    await message.answer(text=lexicon.take.post())
    await state.set_state(FSMPosts.take_post)


@router.message(F.photo, StateFilter(FSMPosts.take_post))
async def test(message: Message, bot: Bot, session: AsyncSession,
               state: FSMContext, lexicon: TranslatorRunner):
    data = await state.get_data()
    name_post = data['name_post']
    await save_photo_post(session, message, bot, name_post)

    if name_post not in cache_ttl.keys():
        cache_ttl[name_post] = True
        keyboard = await get_back_to_post_groups_keyboard(lexicon)
        await message.answer(text=lexicon.post.added(name=name_post), reply_markup=keyboard)


@router.message(F.text, StateFilter(FSMPosts.take_post))
async def process_hello_message(message: Message, session: AsyncSession,
                                state: FSMContext, lexicon: TranslatorRunner):
    data = await state.get_data()
    name_post = data['name_post']
    await save_text_post(session, message.text, message.media_group_id, name_post)

    if name_post not in cache_ttl.keys():
        cache_ttl[name_post] = True
        keyboard = await get_back_to_post_groups_keyboard(lexicon)
        await message.answer(text=lexicon.post.added(name=name_post), reply_markup=keyboard)


@router.message(or_f(F.video, F.voice, F.document, F.audio), StateFilter(FSMPosts.take_post))
async def process_video_message(message: Message, session: AsyncSession, bot: Bot,
                                state: FSMContext, lexicon: TranslatorRunner):
    data = await state.get_data()
    name_post = data['name_post']
    await save_media_post(session, message, bot, name_post)

    if name_post not in cache_ttl.keys():
        cache_ttl[name_post] = True
        keyboard = await get_back_to_post_groups_keyboard(lexicon)
        await message.answer(text=lexicon.post.added(name=name_post), reply_markup=keyboard)


@router.message(F.video_note, StateFilter(FSMPosts.take_post))
async def process_none(message: Message, session: AsyncSession, bot: Bot,
                       state: FSMContext, lexicon: TranslatorRunner):
    data = await state.get_data()
    name_post = data['name_post']
    await save_video_note(session, message, bot, name_post)

    if name_post not in cache_ttl.keys():
        cache_ttl[name_post] = True
        keyboard = await get_back_to_post_groups_keyboard(lexicon)
        await message.answer(text=lexicon.post.added(name=name_post), reply_markup=keyboard)
