from typing import List
from datetime import datetime, time

from pydantic import BaseModel, computed_field, field_validator
from pytz import timezone, utc, UnknownTimeZoneError


class IntervalException(Exception):
    """Base class for other Interval exceptions"""
    pass


class InvalidTimeFormatException(IntervalException):
    """Raised when the time format is invalid"""
    def __init__(self, time_str, message="Time format must be either HH:MM or HH.MM"):
        self.time_str = time_str
        self.message = message
        super().__init__(self.message)


class InvalidIntervalException(IntervalException):
    """Raised when the interval is invalid"""
    def __init__(self, start_time, end_time, message="Start time must be earlier than end time"):
        self.start_time = start_time
        self.end_time = end_time
        self.message = message
        super().__init__(self.message)


class Interval(BaseModel):
    start_time: time
    end_time: time
    tz: str = "UTC"

    @computed_field
    @property
    def start_time_utc(self) -> time:
        return self.convert_to_utc(self.start_time)

    @computed_field
    @property
    def end_time_utc(self) -> time:
        return self.convert_to_utc(self.end_time)

    @field_validator("tz")
    def zone_must_be_valid(cls, tz: str):
        try:
            timezone(tz)
        except UnknownTimeZoneError:
            raise ValueError("You should pass valid zone name")

    def convert_to_utc(self, local_time: time) -> time:
        local_dt = datetime.combine(datetime.today(), local_time).replace(tzinfo=timezone(self.tz))
        utc_dt = local_dt.astimezone(utc)
        return utc_dt.time()

    @classmethod
    def from_string(cls, interval_str: str, tz: str = "UTC"):
        start_str, end_str = interval_str.replace(" ", "").split('-')
        start_time = cls.parse_time(start_str)
        end_time = cls.parse_time(end_str)

        if start_time >= end_time:
            raise InvalidIntervalException(start_time, end_time)

        return cls(start_time=start_time, end_time=end_time, tz=tz)

    @staticmethod
    def parse_time(time_str: str) -> time:
        try:
            if ':' in time_str:
                return datetime.strptime(time_str, "%H:%M").time()
            elif '.' in time_str:
                return datetime.strptime(time_str, "%H.%M").time()
            else:
                raise InvalidTimeFormatException(time_str)
        except ValueError:
            raise InvalidTimeFormatException(time_str)

    def convert_to_timezone(self, new_tz: str):
        start_dt = datetime.combine(datetime.today(), self.start_time).replace(tzinfo=timezone(self.tz))
        end_dt = datetime.combine(datetime.today(), self.end_time).replace(tzinfo=timezone(self.tz))
        new_start_dt = start_dt.astimezone(timezone(new_tz))
        new_end_dt = end_dt.astimezone(timezone(new_tz))
        return Interval(start_time=new_start_dt.time(), end_time=new_end_dt.time(), tz=new_tz)

    def to_string(self):
        return f"{self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"

    def __hash__(self):
        return hash((self.start_time_utc, self.end_time_utc))

    def __eq__(self, other):
        if not isinstance(other, Interval):
            return False
        return (self.start_time_utc == other.start_time_utc and
                self.end_time_utc == other.end_time_utc)

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return f"Interval({self.to_string()}, tz={self.tz})"

    def overlaps_with(self, other):
        start_a = self.start_time_utc
        end_a = self.end_time_utc
        start_b = other.start_time_utc
        end_b = other.end_time_utc

        return max(start_a, start_b) < min(end_a, end_b)

    @staticmethod
    def merge_intervals(intervals):
        distinct_tzs = set([timezone(interval.tz).utcoffset(datetime.now()) for interval in intervals])

        if len(distinct_tzs) != 1:
            raise ValueError("Intervals have to have same timezone offset")

        if not intervals:
            return []

        # Sort intervals by start time
        sorted_intervals = sorted(intervals, key=lambda x: x.start_time)

        merged_intervals = [sorted_intervals[0]]
        for current in sorted_intervals[1:]:
            last = merged_intervals[-1]

            if current.overlaps_with(last) or current.start_time <= last.end_time:
                # Merge intervals
                merged_intervals[-1] = Interval(
                    start_time=min(last.start_time, current.start_time),
                    end_time=max(last.end_time, current.end_time),
                    tz=last.tz
                )
            else:
                merged_intervals.append(current)

        return merged_intervals


class DaySchedule(BaseModel):
    name: str
    included: bool = True
    intervals: List[Interval] = []

    def toggle_inclusion(self):
        self.included = not self.included

    def add_interval(self, interval: Interval):
        self.intervals.append(interval)

    def remove_interval(self, interval: Interval):
        self.intervals = [i for i in self.intervals if i != interval]
