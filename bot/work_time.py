from datetime import datetime

from aiogram import Bot, Router
from aiogram.filters.command import Command
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .commands import bot_command_names
from .custom_types import SendMessage
from .filters import HasChatState, HasMessageText, HasMessageUserUsername
from .keyboards import Interval, DaySchedule, WeekSchedule
from .state import ChatState, save_state, get_user, load_user_pm, create_user_pm, save_user_pm


def handle_working_time(
        scheduler: AsyncIOScheduler, send_message: SendMessage, router: Router, bot: Bot
):
    @router.message(
        Command(bot_command_names.set_personal_working_time), HasMessageUserUsername(), HasChatState()
    )
    async def show_user_schedule(
            message: Message, username: str, chat_state: ChatState
    ):
        my_schedule = {
            "Monday": DaySchedule("Monday", True, [Interval.from_string("09:00 - 18:00")]),
            "Tuesday": DaySchedule("Tuesday", False),
            "Wednesday": DaySchedule("Wednesday", True, [Interval.from_string("10:00 - 17:00")]),
            "Thursday": DaySchedule("Thursday", False),
            "Friday": DaySchedule("Friday", True, [Interval.from_string("09:00 - 18:00")]),
            "Saturday": DaySchedule("Saturday", False),
            "Sunday": DaySchedule("Sunday", False)
        }

        week_schedule = WeekSchedule(schedule=my_schedule)

        await message.answer(
            text=f"@{username}, here is your schedule:",
            reply_markup=week_schedule.to_keyboard()
        )
