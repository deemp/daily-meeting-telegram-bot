import logging
from datetime import datetime

from aiogram import Bot
from aiogram.utils.i18n import gettext as _
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .constants import day_of_week, jobstore
from .custom_types import ChatId, SendMessage
from .messages import make_daily_messages
from .state import ChatState, load_state, get_joined_users


async def send_meeting_messages(chat_id: ChatId, send_message: SendMessage):
    chat_state = await load_state(chat_id=chat_id)
    topic_id = chat_state.topic_id
    current_day = datetime.now().weekday()
    await send_message(chat_id=chat_id, message=_("Meeting time!"), message_thread_id=topic_id)
     
    joined_users = await get_joined_users(chat_state)
    today_workers = [user for user in joined_users if current_day in user.meeting_days]
    if not today_workers:
        await send_message(chat_id=chat_id, message=_("Nobody has joined the meeting!"), message_thread_id=topic_id)
    else:
        for user in today_workers:
            for message in make_daily_messages(username=user.username):
                await send_message(chat_id=chat_id, message=message, message_thread_id=topic_id)


def make_job_id(some_id: int):
    return str(some_id)


def schedule_meeting(
    meeting_time: datetime,
    chat_id: ChatId,
    scheduler: AsyncIOScheduler,
    send_message: SendMessage,
):
    scheduler.add_job(
        jobstore=jobstore,
        func=send_meeting_messages,
        id=make_job_id(chat_id),
        replace_existing=True,
        kwargs={"chat_id": chat_id, "send_message": send_message},
        trigger="cron",
        start_date=meeting_time,
        hour=meeting_time.hour,
        minute=meeting_time.minute,
        day_of_week=day_of_week,
        timezone=meeting_time.tzinfo,
        misfire_grace_time=42,
    )

    logging.info(scheduler.get_job(make_job_id(chat_id)))
