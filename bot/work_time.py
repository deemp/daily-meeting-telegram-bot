import re
from datetime import datetime

from aiogram import Bot, Router, F
from aiogram.filters.command import Command
from aiogram.types import Message, InlineQuery, CallbackQuery, InlineQueryResultArticle, InputTextMessageContent
from aiogram.utils.i18n import gettext as _
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone, utc

from .commands import bot_command_names
from .custom_types import SendMessage
from .callbacks import IntervalCallback, WeekdayCallback
# from .intervals import WeekSchedule, DaySchedule, Interval
from .filters import HasChatState, HasMessageUserUsername
from .keyboards import get_schedule_keyboard
from .state import ChatState, save_state, get_user, load_user_pm, create_user_pm, save_user_pm


EDIT_HANDLE_IVL = \
    r'^edit\s+\w+\s+\d{1,2}[:.]\d{2}\s*-\s*\d{1,2}[:.]\d{2}\s*-->\s*\d{1,2}[:.]\d{2}\s*-\s*\d{1,2}[:.]\d{2}$'

EDIT_PARSE_IVL = \
    r'^edit\s+(?P<weekday>\w+)\s+(?P<start_time1>\d{1,2}[:.]\d{2})\s*-\s*(?P<end_time1>\d{1,2}[:.]\d{2})\s*-->' \
    r'\s*(?P<start_time2>\d{1,2}[:.]\d{2})\s*-\s*(?P<end_time2>\d{1,2}[:.]\d{2})$'

ADD_HANDLE_IVL = r'^add\s+\w+\s+\d{1,2}[:.]\d{2}\s*-\s*\d{1,2}[:.]\d{2}$'
ADD_IVL = r'^add\s+(?P<weekday>\w+)\s+(?P<start_time>\d{1,2}[:.]\d{2})\s*-\s*(?P<end_time>\d{1,2}[:.]\d{2})$'

schedule_db = {
            "Monday": {
                "include": True,
                "intervals": ["9:00 - 18:00"]
            },
            "Tuesday": {
                "include": False,
                "intervals": []
            },
            "Wednesday": {
                "include": True,
                "intervals": ["10:00 - 17:00"]
            },
            "Thursday": {
                "include": False,
                "intervals": []
            },
            "Friday": {
                "include": True,
                "intervals": ["9:00 - 18:00"]
            },
            "Saturday": {
                "include": False,
                "intervals": []
            },
            "Sunday": {
                "include": False,
                "intervals": []
            },
        }

chat_db = {
    "schedule_msg": None,
    "tz": timezone("Europe/Moscow"),
    "shift": 0
}


def handle_working_time(
        scheduler: AsyncIOScheduler, send_message: SendMessage, router: Router, bot: Bot
):
    @router.message(Command(bot_command_names.set_personal_working_time), HasMessageUserUsername(), HasChatState())
    async def show_user_schedule(message: Message, username: str, chat_state: ChatState):
        # sch = WeekSchedule(schedule_db, tz=utc, shift=0)
        for weekday in schedule_db:
            if len(schedule_db[weekday]["intervals"]) == 0 and schedule_db[weekday]["include"]:
                schedule_db[weekday]["intervals"].append("23:59 - 23:59")

        layout = get_schedule_keyboard(schedule_db)
        schedule_msg = await message.answer(f"@{username}, here is your schedule", reply_markup=layout)
        chat_db["schedule_msg"] = schedule_msg

    @router.inline_query(F.query.regexp(EDIT_HANDLE_IVL))
    async def show_inline_interval_editing(inline_query: InlineQuery):

        suggestion = InlineQueryResultArticle(
            id=inline_query.query,
            title=inline_query.query,
            input_message_content=InputTextMessageContent(
                message_text=inline_query.query
            )
        )
        await inline_query.answer([suggestion], is_personal=True)

    @router.message(F.text.regexp(EDIT_HANDLE_IVL), HasMessageUserUsername(), HasChatState())
    async def handle_interval_editing(message: Message, username: str, chat_state: ChatState):

        parse_pattern = re.compile(EDIT_PARSE_IVL)
        parse_match = parse_pattern.match(message.text)
        if parse_match:
            weekday = parse_match.group("weekday")
            st_time_prev = parse_match.group("start_time1")
            end_time_prev = parse_match.group("end_time1")
            st_time_edit = parse_match.group("start_time2")
            end_time_edit = parse_match.group("end_time2")

            interval_prev = f"{st_time_prev} - {end_time_prev}"
            interval_edit = f"{st_time_edit} - {end_time_edit}"

            intervals = schedule_db[weekday]["intervals"]
            if interval_prev in intervals:
                intervals.remove(interval_prev)
                intervals.append(interval_edit)
                schedule_db[weekday]["intervals"] = intervals

            layout = get_schedule_keyboard(schedule_db)
            if chat_db["schedule_msg"]:
                old_msg = chat_db["schedule_msg"]
                await old_msg.edit_reply_markup(reply_markup=layout)

            await message.delete()

    @router.callback_query(IntervalCallback.filter(F.action == 'add'))
    async def add_interval(cb: CallbackQuery, callback_data: IntervalCallback):

        weekday = callback_data.weekday
        schedule_db[weekday]["intervals"].append("23:59 - 23:59")

        layout = get_schedule_keyboard(schedule_db)
        await cb.message.edit_reply_markup(reply_markup=layout)

    @router.callback_query(IntervalCallback.filter(F.action == 'remove'))
    async def remove_interval(cb: CallbackQuery, callback_data: IntervalCallback):

        weekday = callback_data.weekday
        interval = callback_data.interval.replace("|", ":")
        schedule_db[weekday]["intervals"].remove(interval)

        if len(schedule_db[weekday]["intervals"]) == 0 and schedule_db[weekday]["include"]:
            schedule_db[weekday]["intervals"].append("23:59 - 23:59")

        layout = get_schedule_keyboard(schedule_db)
        await cb.message.edit_reply_markup(reply_markup=layout)

    @router.callback_query(WeekdayCallback.filter(F.action == 'toggle'))
    async def toggle_weekday(cb: CallbackQuery, callback_data: WeekdayCallback):

        weekday = callback_data.weekday
        schedule_db[weekday]["include"] = not schedule_db[weekday]["include"]

        if len(schedule_db[weekday]["intervals"]) == 0 and schedule_db[weekday]["include"]:
            schedule_db[weekday]["intervals"].append("23:59 - 23:59")

        layout = get_schedule_keyboard(schedule_db)
        await cb.message.edit_reply_markup(reply_markup=layout)
