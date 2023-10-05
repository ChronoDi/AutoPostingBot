import calendar
import itertools

from datetime import datetime

month_abbr = {
    '1': 'Jan',
    '2': 'Feb',
    '3': 'Mar',
    '4': 'Apr',
    '5': 'May',
    '6': 'Jun',
    '7': 'Jul',
    '8': 'Aug',
    '9': 'Sep',
    '10': 'Oct',
    '11': 'Nov',
    '12': 'Dec'
}


def get_current_year() -> int:
    return datetime.now().year


def get_remaining_months(year: int) -> dict[str, str]:
    if year == datetime.now().year:
        current_month = datetime.now().month
        remaining_months = dict(itertools.islice(month_abbr.items(), current_month - 1, 13))
        return remaining_months

    return month_abbr


def get_remaining_day(year: int, month: int) -> dict[str, str]:
    _, days = calendar.monthrange(year, month)
    days_dict: dict[str, str] = {}
    start_day = datetime.now().day if  year == datetime.now().year and month == datetime.now().month \
                                   else 1

    for i in range(start_day, days + 1):
        days_dict.update({str(i): str(i)})

    return days_dict


def get_current_time() -> tuple[int, int]:
    current_time = datetime.now()
    current_minute = current_time.minute
    current_hour = current_time.hour

    return current_hour, current_minute

def change_time(data: str, hour: int, minute: int) -> tuple[int, int]:
    match data:
        case 'hour_up':
            hour = hour + 1 if hour < 23 else 0
        case 'hour_down':
            hour = hour - 1 if hour > 0 else 23
        case 'minute_up':
            minute = minute + 1 if minute < 59 else 0
        case 'minute_down':
            minute = minute - 1 if minute > 0 else 59

    return hour, minute


def try_get_future_date(year: int, month: int, day: int, hour: int, minute: int) -> tuple[bool, datetime]:
    current_date = datetime.now()
    input_date = datetime(year, month, day, hour, minute)

    print(input_date)

    return input_date > current_date, input_date

