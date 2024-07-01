import re
from textwrap import dedent
from datetime import datetime

from aiogram import Bot, Router, F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineQuery, CallbackQuery, InlineQueryResultArticle, InputTextMessageContent
from aiogram.utils.i18n import gettext as _
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .commands import bot_command_names
from .custom_types import SendMessage
from .messages import make_interval_validation_message
from .callbacks import IntervalCallback, WeekdayCallback
from .constants import interval_format, sample_interval
from .intervals import Interval
from .filters import HasChatState, HasMessageUserUsername, HasMessageText
from .keyboards import get_schedule_keyboard, get_interval_error_keyboard
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
            }
        }

chat_db = {
    "default_working_time": "9:00 - 17:00",
    "personal_default_working_time": "8:00 - 18:00",
    "schedule_msg": None,
    "tz": "Europe/Moscow",
    "shift": 0,
    "edit_interval_message": None,
    "message_with_keyboard": None
}


def handle_working_time(
        scheduler: AsyncIOScheduler, send_message: SendMessage, router: Router, bot: Bot
):
    @router.message(Command(bot_command_names.set_default_working_time), HasMessageText())
    async def set_default_working_time(message: Message, message_text: str):
        cmd = "/" + bot_command_names.set_default_working_time
        interval = message_text.replace(cmd, "").strip()

        is_valid, status_msg = make_interval_validation_message(interval_str=interval, tz="UTC")
        if is_valid:
            chat_db["default_working_time"] = interval
            await message.answer(
                _(
                    "Your group default working time is set to {interval}"
                ).format(interval=interval)
            )
        else:
            await message.answer(
                dedent(
                    _(
                        f"""
                        Please write group default working time in {interval_format} format.
                        
                        Example:
                        
                        /{set_default_working_time} {sample_interval}
                        """
                    ).format(
                        interval_format=interval_format,
                        set_default_working_time=bot_command_names.set_default_working_time,
                        sample_interval=sample_interval
                    )
                )
            )

    @router.message(Command(bot_command_names.set_personal_default_working_time), HasMessageText())
    async def set_personal_default_working_time(message: Message, message_text: str):
        cmd = "/" + bot_command_names.set_personal_default_working_time
        interval = message_text.replace(cmd, "").strip()

        is_valid, status_msg = make_interval_validation_message(interval_str=interval, tz="UTC")
        if is_valid:
            chat_db["personal_default_working_time"] = interval
            await message.answer(
                _(
                    "Your personal default working time is set to {interval}"
                ).format(interval=interval)
            )
        else:
            await message.answer(
                dedent(
                    _(
                        f"""
                            Please write your personal default working time in {interval_format} format.

                            Example:

                            /{set_personal_default_working_time} {sample_interval}
                            """
                    ).format(
                        interval_format=interval_format,
                        set_default_working_time=bot_command_names.set_personal_default_working_time,
                        sample_interval=sample_interval
                    )
                )
            )

    @router.message(Command(bot_command_names.set_personal_working_time), HasMessageUserUsername(), HasChatState())
    async def show_user_schedule(message: Message, username: str, chat_state: ChatState):
        personal_default_interval = chat_db["personal_default_working_time"]
        group_default_interval = chat_db["default_working_time"]

        if personal_default_interval is not None or group_default_interval is not None:
            default = personal_default_interval if personal_default_interval is not None else group_default_interval

            for weekday in schedule_db:
                if len(schedule_db[weekday]["intervals"]) == 0 and schedule_db[weekday]["include"]:
                    schedule_db[weekday]["intervals"].append(default)

            layout = get_schedule_keyboard(schedule_db)
            schedule_msg = await message.answer(f"@{username}, here is your schedule", reply_markup=layout)
            chat_db["schedule_msg"] = schedule_msg
        else:
            await message.answer("You should set up default group or personal working time first!")

    @router.inline_query(F.query.regexp(EDIT_HANDLE_IVL))
    async def show_inline_interval_editing(inline_query: InlineQuery):
        message_with_keyboard = chat_db["message_with_keyboard"]
        edit_interval_message = chat_db["edit_interval_message"]

        if message_with_keyboard is not None and edit_interval_message is not None:
            await message_with_keyboard.delete()
            await edit_interval_message.delete()

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

            is_valid, status_msg = make_interval_validation_message(interval_str=interval_edit, tz=chat_db["tz"])

            if is_valid:

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

            else:
                layout = get_interval_error_keyboard(interval_prev, weekday)
                keyboard_msg = await message.reply(text=status_msg, reply_markup=layout)

                chat_db["edit_interval_message"] = message
                chat_db["message_with_keyboard"] = keyboard_msg

    @router.callback_query(IntervalCallback.filter(F.action == 'add'))
    async def add_interval(cb: CallbackQuery, callback_data: IntervalCallback):

        personal_default_interval = chat_db["personal_default_working_time"]
        group_default_interval = chat_db["default_working_time"]
        default = personal_default_interval if personal_default_interval is not None else group_default_interval

        weekday = callback_data.weekday
        schedule_db[weekday]["intervals"].append(default)

        layout = get_schedule_keyboard(schedule_db)
        await cb.message.edit_reply_markup(reply_markup=layout)

    @router.callback_query(IntervalCallback.filter(F.action == 'remove'))
    async def remove_interval(cb: CallbackQuery, callback_data: IntervalCallback):
        personal_default_interval = chat_db["personal_default_working_time"]
        group_default_interval = chat_db["default_working_time"]
        default = personal_default_interval if personal_default_interval is not None else group_default_interval

        weekday = callback_data.weekday
        interval = callback_data.interval.replace("|", ":")
        schedule_db[weekday]["intervals"].remove(interval)

        if len(schedule_db[weekday]["intervals"]) == 0 and schedule_db[weekday]["include"]:
            schedule_db[weekday]["intervals"].append(default)

        layout = get_schedule_keyboard(schedule_db)
        await cb.message.edit_reply_markup(reply_markup=layout)

    @router.callback_query(WeekdayCallback.filter(F.action == 'toggle'))
    async def toggle_weekday(cb: CallbackQuery, callback_data: WeekdayCallback):
        personal_default_interval = chat_db["personal_default_working_time"]
        group_default_interval = chat_db["default_working_time"]
        default = personal_default_interval if personal_default_interval is not None else group_default_interval

        weekday = callback_data.weekday
        schedule_db[weekday]["include"] = not schedule_db[weekday]["include"]

        if len(schedule_db[weekday]["intervals"]) == 0 and schedule_db[weekday]["include"]:
            schedule_db[weekday]["intervals"].append(default)

        layout = get_schedule_keyboard(schedule_db)
        await cb.message.edit_reply_markup(reply_markup=layout)

    @router.callback_query(F.data == "cancel_editing_interval")
    async def cancel_editing_interval(cb: CallbackQuery):
        message_with_keyboard = cb.message
        edit_interval_message = cb.message.reply_to_message

        await message_with_keyboard.delete()
        await edit_interval_message.delete()
