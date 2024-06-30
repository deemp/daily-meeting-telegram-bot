from typing import List, Dict
from datetime import datetime, time

from pydantic import BaseModel, computed_field
from pytz import timezone, utc


class Interval(BaseModel):
    start_time: time
    end_time: time
    tz: timezone = utc

    @computed_field
    @property
    def start_time_utc(self) -> time:
        return self.convert_to_utc(self.start_time)

    @computed_field
    @property
    def end_time_utc(self) -> time:
        return self.convert_to_utc(self.end_time)

    def convert_to_utc(self, local_time: time) -> time:
        local_dt = datetime.combine(datetime.today(), local_time).replace(tzinfo=self.tz)
        utc_dt = local_dt.astimezone(utc)
        return utc_dt.time()

    @classmethod
    def from_string(cls, interval_str: str, tz: timezone):
        start_str, end_str = interval_str.replace(" ", "").split('-')
        start_time = cls.parse_time(start_str)
        end_time = cls.parse_time(end_str)
        return cls(start_time=start_time, end_time=end_time, tz=tz)

    @staticmethod
    def parse_time(time_str: str) -> time:
        if ':' in time_str:
            return datetime.strptime(time_str, "%H:%M").time()
        elif '.' in time_str:
            return datetime.strptime(time_str, "%H.%M").time()
        else:
            raise ValueError("Time format must be either HH:MM or HH.MM")

    def convert_to_timezone(self, new_tz: timezone):
        start_dt = datetime.combine(datetime.today(), self.start_time).replace(tzinfo=self.tz)
        end_dt = datetime.combine(datetime.today(), self.end_time).replace(tzinfo=self.tz)
        new_start_dt = start_dt.astimezone(new_tz)
        new_end_dt = end_dt.astimezone(new_tz)
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
        distinct_tzs = set([interval.tz for interval in intervals])

        if len(distinct_tzs) != 1:
            raise ValueError("Intervals have to have same tz")

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


class WeekSchedule(BaseModel):
    self.schedule: Dict[str, DaySchedule] = dict()
    self.tz = tz
    self.shift = shift

    for weekday in schedule:

        intervals = []
        for interval in schedule[weekday]["intervals"]:
            intervals.append(Interval.from_string(interval, self.tz))

        day_schedule = DaySchedule(weekday, schedule[weekday]["include"], intervals)
        self.schedule[weekday] = day_schedule
