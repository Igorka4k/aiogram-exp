import datetime

from dateutil.tz import gettz

from functions.timetable.tools import *
from base_template.context import *
from base_template.db.queries import *

ADMIN_CHAT = list(map(int, environ.get('ADMIN_CHAT').split(',')))
TIMEZONE = gettz('Asia/Yekaterinburg')


def schedule_notify(when, time: str, date: str, chat_id=None, callback=None):
    from base_template.bot import updater
    all_the_timer = get_timedelta(when)
    day_before_timer = all_the_timer - datetime.timedelta(days=1)
    two_hours_before_timer = all_the_timer - datetime.timedelta(hours=2)
    clear_timer = all_the_timer
    if callback is None:
        updater.job_queue.run_once(callback=day_before_notify, when=day_before_timer, context=chat_id)
        updater.job_queue.run_once(callback=two_hours_before_notify,
                                   when=two_hours_before_timer,
                                   context=chat_id)

        updater.job_queue.run_once(callback=clear_appointment_callback,
                                   when=clear_timer,
                                   context=(time, date))
    else:
        updater.job_queue.run_once(callback=callback, when=clear_timer, context=date)

    updater.job_queue.start()
    updater.job_queue.jobs()


def day_before_notify(ctx):
    rows = get_data(db_connect())[-1]
    dt = datetime.timedelta(days=1)
    check_timer = datetime.timedelta(minutes=5)
    this_user = False
    this_time = False
    for row in rows:
        if int(row['chat_id']) == int(ctx.job.context):
            this_user = True
            day, month, year = row['date'].split("-")
            appointments_time = get_datetime_from_formatting(f"{day}-{month}-{year}, {row['time']}")

            if dt - check_timer <= get_timedelta(appointments_time) <= dt:
                this_time = True
            break
    if this_user and this_time:
        ctx.bot.send_message(chat_id=ctx.job.context,
                             text=day_before_notify_msg)
        for chat_id in ADMIN_CHAT:
            ctx.bot.send_message(chat_id=chat_id, text=day_before_notify_msg_admin)


def two_hours_before_notify(ctx):
    rows = get_data(db_connect())[-1]
    dt = datetime.timedelta(hours=2)
    check_timer = datetime.timedelta(minutes=5)
    this_user = False
    this_time = False
    for row in rows:
        if int(row['chat_id']) == int(ctx.job.context):
            this_user = True
            day, month, year = row['date'].split("-")
            appointments_time = get_datetime_from_formatting(f"{day}-{month}-{year}, {row['time']}")
            if dt - check_timer <= get_timedelta(appointments_time) <= dt:
                this_time = True
            break
    if this_user and this_time:
        ctx.bot.send_message(chat_id=ctx.job.context,
                             text=day_before_notify_msg)
        for chat_id in ADMIN_CHAT:
            ctx.bot.send_message(chat_id=chat_id, text=two_hours_before_notify_msg_admin)


def clear_appointment_callback(ctx):
    clear_appointment(db_connect(), ctx.job.context)


def clear_the_holidays_callback(ctx):
    clear_holidays(db_connect(), ctx.job.context)
