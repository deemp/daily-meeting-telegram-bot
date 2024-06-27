from typing import List, Dict, Optional
from datetime import datetime, time

from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup, InlineKeyboardButton
from pytz import timezone, utc

INCLUDED_1 = "✅"
INCLUDED_2 = "🗹"
INCLUDED_3 = "🟩"
NOT_INCLUDED_1 = "❎"
NOT_INCLUDED_2 = "☐"
NOT_INCLUDED_3 = "🟥"
ADD = "➕"
REMOVE = "✖️"


# TODO: merge overlapping intervals
# TODO: sort intervals
class Interval:
    def __init__(self, start_time: time, end_time: time, tz: timezone = utc):
        self.start_time = start_time
        self.end_time = end_time
        self.tz = tz

    @classmethod
    def from_string(cls, interval_str: str, tz: timezone = utc):
        start_str, end_str = interval_str.replace(" ", "").split('-')
        start_time = cls.parse_time(start_str)
        end_time = cls.parse_time(end_str)
        return cls(start_time, end_time, tz)

    @staticmethod
    def parse_time(time_str: str) -> time:
        if ':' in time_str:
            return datetime.strptime(time_str, "%H:%M").time()
        elif '.' in time_str:
            return datetime.strptime(time_str, "%H.%M").time()
        else:
            raise ValueError("Time format must be either HH:MM or HH.MM")

    def to_string(self):
        return f"{self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"

    def convert_to_timezone(self, new_tz: timezone):
        start_dt = datetime.combine(datetime.today(), self.start_time).replace(tzinfo=self.tz)
        end_dt = datetime.combine(datetime.today(), self.end_time).replace(tzinfo=self.tz)
        new_start_dt = start_dt.astimezone(new_tz)
        new_end_dt = end_dt.astimezone(new_tz)
        self.start_time = new_start_dt.time()
        self.end_time = new_end_dt.time()
        self.tz = new_tz

    def overlaps_with(self, other):
        if self.tz != other.tz:
            raise ValueError("Time zones must match to compare intervals")

        start_a = datetime.combine(datetime.today(), self.start_time)
        end_a = datetime.combine(datetime.today(), self.end_time)
        start_b = datetime.combine(datetime.today(), other.start_time)
        end_b = datetime.combine(datetime.today(), other.end_time)

        return max(start_a, start_b) < min(end_a, end_b)

    def to_keyboard(self, weekday: str) -> InlineKeyboardBuilder:
        builder = InlineKeyboardBuilder()
        interval_str = self.to_string()

        builder.button(text=interval_str, callback_data=f"{weekday}_interval_{interval_str}")
        builder.button(text=REMOVE, callback_data=f"{weekday}_remove_{interval_str}")
        builder.button(text=ADD, callback_data=f"{weekday}_add")
        builder.adjust(3)

        return builder

    def __eq__(self, other):
        if not isinstance(other, Interval):
            return False
        return (self.start_time == other.start_time and
                self.end_time == other.end_time and
                self.tz == other.tz)

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return f"Interval({self.to_string()}, tz={self.tz})"


class DaySchedule:
    def __init__(self, name: str, included: bool = False, intervals: Optional[List[Interval]] = None):
        self.name = name
        self.included = included
        self.intervals: List[Interval] = intervals if intervals else []

    def toggle_inclusion(self):
        self.included = not self.included

    def add_interval(self, interval: Interval):
        self.intervals.append(interval)

    def remove_interval(self, interval: Interval):
        self.intervals = [i for i in self.intervals if i != interval]

    def to_keyboard(self) -> InlineKeyboardBuilder:
        builder = InlineKeyboardBuilder()
        included_text = INCLUDED_3 if self.included else NOT_INCLUDED_3

        day = InlineKeyboardButton(text=f"{self.name}", callback_data=f"{self.name}")
        status = InlineKeyboardButton(text=included_text, callback_data=f"{self.name}_toggle")
        builder.row(day, status)

        if self.included:
            for interval in self.intervals:
                interval_builder = interval.to_keyboard(weekday=self.name)
                builder.attach(interval_builder)

        return builder


class WeekSchedule:
    def __init__(self, schedule: Dict[str, DaySchedule]):
        self.schedule = schedule

    def to_keyboard(self) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        for weekday in self.schedule.values():
            weekday_builder = weekday.to_keyboard()
            builder.attach(weekday_builder)

        return builder.as_markup()
