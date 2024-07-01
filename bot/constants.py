from aiogram import html
from bot.intervals import DaySchedule

ENCODING = "utf-8"


class AppCommands:
    print_bot_message = "print-bot-message"
    print_meeting_messages = "print-meeting-messages"
    start = "start"


jobstore = "bot_jobs"

time_url = "https://time.lol"

iso8601 = "ISO 8601"

interval_format = "HH:MM or HH.MM"

sample_interval = "9:00 - 17:00"

datetime_time_format = "%H:%M %Y-%m-%d"

day_of_week = "0-6"

day_of_week_pretty = "Monday - Friday"

day_of_week_to_num = {
    "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6
}

sample_time = "2024-06-03T14:00:00+03:00"

default_time_zone = "Europe/Moscow"

days_array = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

empty_day_schedule = [DaySchedule() for _ in range(len(days_array))]

for i in range(len(days_array)):
    empty_day_schedule[i].name = days_array[i]

default_user_schedule = empty_day_schedule
