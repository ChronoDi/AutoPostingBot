from aiogram.types import InlineKeyboardMarkup
from fluentogram import TranslatorRunner

from tg_bot.keyboards.fabric import get_inline_keyboards
from tg_bot.utils.calendar import get_current_year, get_remaining_months, get_remaining_day


def get_years_keyboard() -> InlineKeyboardMarkup:
    current_year: int = get_current_year()
    years_dict: dict[str, str] = {}

    for i in range(current_year, current_year + 3):
        years_dict.update({str(i) : str(i)})

    return get_inline_keyboards(width=3, callback_names=years_dict)


def get_month_keyboard(year: int) -> InlineKeyboardMarkup:
    month_dict = get_remaining_months(year)

    return get_inline_keyboards(width=6, callback_names=month_dict)


def get_days_keyboard(year: int, month: int) -> InlineKeyboardMarkup:
    days_dict = get_remaining_day(year, month)

    return get_inline_keyboards(width=7, callback_names=days_dict)

def time_keyboard(hours : int, minutes: int, lexicon: TranslatorRunner) -> InlineKeyboardMarkup:
    time_dict = {
        'hour_down' : '<<', 'hours' : str(hours), 'hour_up' : '>>',
        'minute_down' : '<<', 'minutes' : str(minutes), 'minute_up' : '>>'
    }

    last_buttons = {'ready' : lexicon.ready()}

    return get_inline_keyboards(width=3, callback_names=time_dict, first_last_buttons=last_buttons)


