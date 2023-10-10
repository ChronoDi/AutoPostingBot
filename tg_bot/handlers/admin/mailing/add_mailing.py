from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.keyboards import get_groups_keyboard
from tg_bot.keyboards.calendar import get_years_keyboard, get_month_keyboard, get_days_keyboard, time_keyboard
from tg_bot.keyboards.mailing import get_to_mailing_keyboard
from tg_bot.keyboards.pagination import get_next_keyboard
from tg_bot.states.mailing import FSMMailing
from tg_bot.utils.cache.cache_access import CacheAccess
from tg_bot.utils.calendar import get_current_time, change_time, try_get_future_date
from tg_bot.utils.database.mailing import create_mailing
from tg_bot.utils.paginator import slice_dict, get_current_page
from tg_bot.utils.process_group import get_group_dict
from tg_bot.utils.sender import send_mailing
from tkq import db_source

router: Router = Router()

@router.callback_query(F.data == 'add', StateFilter(FSMMailing.view_mailing))
@router.callback_query(F.data == 'date', StateFilter(FSMMailing.view_mailing_menu))
async def process_add_mailing(callback: CallbackQuery, lexicon: TranslatorRunner, state: FSMContext):
    if callback.data == 'add':
        await state.update_data(edit=0)
    else:
        await state.update_data(edit=1)

    keyboard = get_years_keyboard()
    await callback.message.edit_text(text=lexicon.select.years(), reply_markup=keyboard)
    await state.set_state(FSMMailing.take_year)


@router.callback_query(StateFilter(FSMMailing.take_year))
async def process_take_year(callback: CallbackQuery, lexicon: TranslatorRunner, state: FSMContext):
    await state.update_data(year=callback.data)
    keyboard = get_month_keyboard(int(callback.data))
    await callback.message.edit_text(text=lexicon.select.month(), reply_markup=keyboard)
    await state.set_state(FSMMailing.take_month)


@router.callback_query(StateFilter(FSMMailing.take_month))
async def process_take_month(callback: CallbackQuery, lexicon: TranslatorRunner, state: FSMContext):
    await state.update_data(month=callback.data)
    data = await state.get_data()
    year = data['year']
    keyboard = get_days_keyboard(int(year), int(callback.data))
    await callback.message.edit_text(text=lexicon.select.day(), reply_markup=keyboard)
    await state.set_state(FSMMailing.take_day)


@router.callback_query(StateFilter(FSMMailing.take_day))
async def process_take_day(callback: CallbackQuery, lexicon: TranslatorRunner, state: FSMContext):
    current_hour, current_minute = get_current_time()
    await state.update_data(hour=current_hour, minute=current_minute, day=callback.data)
    keyboard = time_keyboard(current_hour, current_minute, lexicon)
    await callback.message.edit_text(text=lexicon.select.time(), reply_markup=keyboard)
    await state.set_state(FSMMailing.take_time)


@router.callback_query(or_f(F.data.contains('up'), F.data.contains('down')), StateFilter(FSMMailing.take_time))
async def process_install_time(callback: CallbackQuery, lexicon: TranslatorRunner, state: FSMContext):
    data = await state.get_data()
    hour = int(data['hour'])
    minute = int(data['minute'])
    hour, minute = change_time(callback.data, hour, minute)
    await state.update_data(hour=hour, minute=minute)
    keyboard = time_keyboard(hour, minute, lexicon)
    await callback.message.edit_text(text=lexicon.select.time(), reply_markup=keyboard)


@router.callback_query(F.data == 'hours', StateFilter(FSMMailing.take_time))
async def process_take_hours(callback: CallbackQuery, lexicon: TranslatorRunner, state: FSMContext):
    await callback.message.edit_text(text=lexicon.select.hours())
    await state.set_state(FSMMailing.take_hours)


@router.message(F.text.isdigit() & F.text.func(lambda text: 0 <= int(text) <= 23),
                StateFilter(FSMMailing.take_hours))
async def process_input_hours(message: Message, lexicon: TranslatorRunner, state: FSMContext):
    data = await state.get_data()
    minute = int(data['minute'])
    keyboard = time_keyboard(int(message.text), minute, lexicon)
    await state.update_data(hour=message.text)
    await message.answer(text=lexicon.select.time(), reply_markup=keyboard)
    await state.set_state(FSMMailing.take_time)


@router.callback_query(F.data == 'minutes', StateFilter(FSMMailing.take_time))
async def process_take_hours(callback: CallbackQuery, lexicon: TranslatorRunner, state: FSMContext):
    await callback.message.edit_text(text=lexicon.select.minutes())
    await state.set_state(FSMMailing.take_minutes)


@router.message(F.text.isdigit() & F.text.func(lambda text: 0 <= int(text) <= 59),
                StateFilter(FSMMailing.take_minutes))
async def process_input_hours(message: Message, lexicon: TranslatorRunner, state: FSMContext):
    data = await state.get_data()
    hours = int(data['hour'])
    keyboard = time_keyboard(hours, int(message.text), lexicon)
    await state.update_data(minute=message.text)
    await message.answer(text=lexicon.select.time(), reply_markup=keyboard)
    await state.set_state(FSMMailing.take_time)


@router.message(F.text, or_f(StateFilter(FSMMailing.take_minutes), StateFilter(FSMMailing.take_hours)))
async def process_error_input(message: Message, lexicon: TranslatorRunner):
    await message.answer(text=lexicon.error.input())


@router.callback_query(F.data == 'ready', StateFilter(FSMMailing.take_time))
async def process_ready_date(callback: CallbackQuery, lexicon: TranslatorRunner, state: FSMContext):
    data = await state.get_data()
    year = int(data['year'])
    day = int(data['day'])
    month = int(data['month'])
    hour = int(data['hour'])
    minute = int(data['minute'])

    is_future, date = try_get_future_date(year, month, day, hour, minute)

    if is_future:
        data = await state.get_data()
        keyboard = await get_next_keyboard()
        await callback.message.edit_text(text=lexicon.date.selected(date=date, time=str(date.time())), reply_markup=keyboard)
        await state.set_state(FSMMailing.time_selected if data['edit'] == 0 else FSMMailing.edit_time)
    else:
        try:
            keyboard = time_keyboard(hour, minute, lexicon)
            await callback.message.edit_text(text=lexicon.wrong.date(), reply_markup=keyboard)
        except TelegramBadRequest:
            await callback.answer()


@router.callback_query(F.data == 'next', StateFilter(FSMMailing.time_selected))
async def process_select_time(callback: CallbackQuery, lexicon: TranslatorRunner, state: FSMContext,
                             session: AsyncSession, cache: CacheAccess):
    group_dict = await get_group_dict(session, cache)
    result_dict, num_pages = slice_dict(group_dict, num_elements=6)
    await state.update_data(result_dict=result_dict, num_pages=num_pages, current_page=0)
    keyboard = await get_groups_keyboard(result_dict['0'])
    await callback.message.edit_text(text=lexicon.select.group(), reply_markup=keyboard)
    await state.set_state(FSMMailing.take_group)


@router.callback_query(or_f(F.data == 'previous', F.data == 'next'), StateFilter(FSMMailing.take_group))
async def process_paginator_groups(callback: CallbackQuery, state: FSMContext, lexicon: TranslatorRunner):
   is_next = True if callback.data == 'next' else False
   posts_group: dict[str: str] = await get_current_page(state, is_next)
   keyboard = await get_groups_keyboard(posts_group)

   try:
      await callback.message.edit_text(text=lexicon.select.group(), reply_markup=keyboard)
   except TelegramBadRequest:
      await callback.answer()


@router.callback_query(StateFilter(FSMMailing.take_group))
async def process_group(callback: CallbackQuery, lexicon: TranslatorRunner, state: FSMContext):
    await state.update_data(group_id=callback.data)
    await callback.message.edit_text(text=lexicon.take.mailing.name())
    await state.set_state(FSMMailing.take_mailing_name)


@router.message(F.text, StateFilter(FSMMailing.take_mailing_name))
async def process_mailing_name(message: Message, session: AsyncSession, state: FSMContext,
                               lexicon: TranslatorRunner):
    name = message.text
    data = await state.get_data()
    year = int(data['year'])
    day = int(data['day'])
    month = int(data['month'])
    hour = int(data['hour'])
    minute = int(data['minute'])
    group_id = int(data['group_id'])

    date, mailing_id = await create_mailing(year=year, month=month, day=day, hour=hour,
                                minute=minute, group_id=group_id, name=name, session=session)
    await db_source.add_task(
        task=send_mailing.kicker().with_labels(),
        time=date,
        mailing_id=mailing_id,
        group_id=group_id
    )
    keyboard = await get_to_mailing_keyboard(lexicon)
    await message.answer(text=lexicon.create.mailing(name=name, date=date), reply_markup=keyboard)
    await state.set_state(FSMMailing.create_mailing)
