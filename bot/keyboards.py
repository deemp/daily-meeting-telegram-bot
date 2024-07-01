from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup, InlineKeyboardButton

from .callbacks import IntervalCallback, WeekdayCallback

INCLUDED_1 = "✅"
INCLUDED_2 = "🗹"
INCLUDED_3 = "🟩"
NOT_INCLUDED_1 = "❎"
NOT_INCLUDED_2 = "☐"
NOT_INCLUDED_3 = "🟥"
ADD = "➕"
REMOVE = "✖️"


def get_interval_keyboard(interval: str, weekday: str) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    interval_std = interval.replace(":", "|")

    builder.button(text=interval, switch_inline_query_current_chat=f"edit  {weekday}  {interval}  -->  {interval}")
    builder.button(text=REMOVE, callback_data=IntervalCallback(weekday=weekday, interval=interval_std, action='remove'))
    builder.button(text=ADD, callback_data=IntervalCallback(weekday=weekday, interval=interval_std, action='add'))
    builder.adjust(3)

    return builder


def get_weekday_keyboard(weekday: str, content: dict) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    included_text = INCLUDED_3 if content["include"] else NOT_INCLUDED_3

    day = InlineKeyboardButton(text=f"{weekday}", callback_data="#")
    status = InlineKeyboardButton(
        text=included_text,
        callback_data=WeekdayCallback(weekday=weekday, action="toggle").pack()
    )

    builder.row(day, status)

    if content["include"]:
        for interval in content["intervals"]:
            interval_builder = get_interval_keyboard(interval, weekday)
            builder.attach(interval_builder)

    return builder


def get_schedule_keyboard(week_schedule: dict) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for weekday, content in week_schedule.items():
        weekday_builder = get_weekday_keyboard(weekday, content)
        builder.attach(weekday_builder)

    return builder.as_markup()


def get_interval_error_keyboard(interval: str, weekday: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="Cancel", callback_data="cancel_editing_interval")
    builder.button(
        text="Enter the interval again",
        switch_inline_query_current_chat=f"edit  {weekday}  {interval}  -->  {interval}"
    )

    return builder.adjust(2).as_markup()
