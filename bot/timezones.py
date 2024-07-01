from datetime import datetime, timedelta, UTC
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pytz import all_timezones, timezone


def guess_time_zone(hour: int, minute: int) -> list[str]:
    utcnow = datetime.now(UTC)
    local = datetime.now(UTC)
    local = local.replace(hour=hour, minute=minute)
    offset = timedelta(days = 0, seconds=(local - utcnow).seconds).total_seconds() // 60

    res_timezones = []
    for time_zone in all_timezones:
        timezone_offset = timezone(time_zone).utcoffset(datetime.now()).total_seconds() // 60
        if timezone_offset == offset:
            res_timezones.append(time_zone)

    return res_timezones


def make_timezones_inline_keybard(timezones: list[str]) -> InlineKeyboardMarkup:
    buttons = []
    counter = 0
    for time_zone in timezones:
        if counter % 3 == 0:
            buttons.append([])
        buttons[counter // 3].append(InlineKeyboardButton(
            text=time_zone,
            callback_data=f"default_time_zone {time_zone}")
        )
        counter += 1
    return InlineKeyboardMarkup(inline_keyboard=buttons)
