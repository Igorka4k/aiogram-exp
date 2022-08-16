# Функционал timetable для админа.
from dateutil.tz import gettz

from base_template.keyboards import *
from functions.timetable.new_calendar.example import calendar_build
from functions.timetable.tools import *
from base_template.decorators import *
from base_template.db import queries
import datetime as dt

import functools

TIMEZONE = gettz('Asia/Yekaterinburg')


@functools.partial(only_table_values, collection=TIMETABLE_HOURS_ADMIN1, keyboard_type="time")
def work_begin_hours_choosing(update, ctx):
    msg = update.message.text
    ctx.user_data['prev_msg'] = msg
    ctx.user_data["work_hours"] = {msg: ''}
    keyboard = ReplyKeyboardMarkup(TIMETABLE_HOURS_ADMIN1, resize_keyboard=True)
    ctx.bot.send_message(chat_id=update.effective_chat.id, text=working_hours_choosing_msg2,
                         reply_markup=keyboard)
    return "work_end_hours_choosing"


@functools.partial(only_table_values, collection=TIMETABLE_HOURS_ADMIN1, keyboard_type="time")
def work_end_hours_choosing(update, ctx):
    msg = update.message.text
    prev = ctx.user_data["prev_msg"]

    # ниже проверка на то, что время может быть выбрано в пределах одного текущего дня:
    if dt.timedelta(hours=int(msg.split(":")[0]), minutes=int(msg.split(":")[1])) <= \
            dt.timedelta(hours=int(prev.split(":")[0]), minutes=int(prev.split(":")[1])):
        two_dates_range = True
    ctx.user_data["work_hours"][ctx.user_data['prev_msg']] = msg

    # ниже идёт выбор обеденного перерыва (недоработанно, не удалять):
    # keyboard = ReplyKeyboardMarkup(YES_NO_KEYBOARD, resize_keyboard=True)
    # ctx.bot.send_message(chat_id=update.effective_chat.id, text="Добавить часы работы? "
    #                                                             "(в случае если рабочий день не закончен)",
    #                      reply_markup=keyboard)

    beginning_time, ending_time = set_working_hours(update, ctx)
    keyboard = ReplyKeyboardMarkup(ONLINE_TIMETABLE_SETTINGS, resize_keyboard=True)
    ctx.bot.send_message(chat_id=update.effective_chat.id, text=f"Готово! теперь к вам можно записаться только"
                                                                f" с {beginning_time} по {ending_time}.",
                         reply_markup=keyboard)
    return "online_appointment_settings"


@functools.partial(only_table_values, collection=TIMETABLE_DURATION, keyboard_type="timetable_range")
def timetable_duration_choosing(update, ctx):
    msg = update.message.text
    if msg == back_btn:
        ctx.bot.send_message(chat_id=update.effective_chat.id, text=timetable_editor_comeback_msg,
                             reply_markup=ReplyKeyboardMarkup(ONLINE_TIMETABLE_SETTINGS, resize_keyboard=True))
        return 'online_appointment_settings'
    if msg == week_range_btn:
        days_value = 7
        queries.set_timetable_range(db_connect(), str(days_value))

    elif msg == one_month_range_btn:
        days_value = 30
        queries.set_timetable_range(db_connect(), str(days_value))
    elif msg == three_month_range_btn:
        days_value = 90
        queries.set_timetable_range(db_connect(), str(days_value))
    elif msg == year_range_btn:
        days_value = 365
        queries.set_timetable_range(db_connect(), str(days_value))
    else:
        days_value = "xxx"
    ctx.user_data['timetable_settings']['timetable_range'] = queries.get_timetable_range(db_connect())
    keyboard = ReplyKeyboardMarkup(ONLINE_TIMETABLE_SETTINGS, resize_keyboard=True)
    ctx.bot.send_message(chat_id=update.effective_chat.id,
                         text=f"Выбран диапазон записи на {msg.lower()}.\n"
                              f"P.S.: Это значит что клиенты могут записаться к вам не более чем на {days_value} "
                              f"дней вперёд.",
                         reply_markup=keyboard)
    return "online_appointment_settings"


def days_off_callback(update, ctx):
    """callback на данный момент отключён, функционал перенесен в bot.py/all_the_callback"""
    query = update.callback_query
    data = query.data
    if data == back_btn:
        ctx.bot.send_message(chat_id=update.effective_chat.id, text=timetable_editor_comeback_msg,
                             reply_markup=ReplyKeyboardMarkup(ONLINE_TIMETABLE_SETTINGS, resize_keyboard=True))
        return 'online_appointment_settings'
    queries.set_days_off(db_connect(), data)
    query.edit_message_text(text=f"Выберите/Уберите нерабочие дни. ([выходные дни])")


def holidays_menu(update, ctx):
    msg = update.message.text
    if msg == back_btn:
        keyboard = ReplyKeyboardMarkup(ONLINE_TIMETABLE_SETTINGS, resize_keyboard=True)
        ctx.bot.send_message(chat_id=update.effective_chat.id, text=timetable_editor_comeback_msg,
                             reply_markup=keyboard)
        return "online_appointment_settings"
    elif msg == holidays_menu_info_btn:
        current_holidays = queries.get_holidays((db_connect()))
        if current_holidays is None:
            msg_to_send = without_holidays_exc_msg__info
        else:
            msg_to_send = f"С {current_holidays['begin_date']} по {current_holidays['end_date']} онлайн-запись будет " \
                          f"недоступна для пользователя, т.к. вы назначили отпуск на этот период."
        ctx.bot.send_message(chat_id=update.effective_chat.id,
                             text=msg_to_send)
        return "holidays_menu"

    elif msg == holidays_menu_cancel_btn:
        cancel_holidays_query = queries.cancel_holidays(db_connect())
        ctx.user_data['timetable_settings']['holidays'] = cancel_holidays_query
        if cancel_holidays_query is None:
            msg_to_send = without_holidays_exc_msg__cancel
        else:
            msg_to_send = f"Запланированный (с {cancel_holidays_query['begin_date']} " \
                          f"по {cancel_holidays_query['end_date']}) отпуск был отменён."
        ctx.bot.send_message(chat_id=update.effective_chat.id,
                             text=msg_to_send)
        return "holidays_menu"

    elif msg == holidays_menu_set_btn:
        if queries.get_holidays(db_connect()) is not None:
            ctx.bot.send_message(chat_id=update.effective_chat.id,
                                 text=with_holidays_exc_msg__setting)
            return "holidays_menu"

        ctx.user_data["choose_holidays"][1] = True
        calendar_build(update, ctx, entry_state="month")
        # нет return потому что дальше функционал зависит от callback`ов.


def set_working_hours(update, ctx):
    chosen_time = min([dt.timedelta(hours=int(i.split(":")[0]),
                                    minutes=int(i.split(":")[1])) for i in ctx.user_data["work_hours"].keys()])
    total_seconds = int(chosen_time.total_seconds())
    hours, remainder = divmod(total_seconds, 60 * 60)
    minutes, seconds = divmod(remainder, 60)

    work_begin_time = dt.time(hour=hours, minute=minutes).strftime("%H:%M")
    work_end_time = ctx.user_data["work_hours"][work_begin_time]
    queries.working_time_adding(db_connect(), work_begin_time, work_end_time)
    ctx.user_data['timetable_settings']['working_hours'] = queries.get_working_hours(db_connect())
    return work_begin_time, work_end_time


def dates_between_range(update, ctx):
    msg = update.message.text
    try:
        if int(msg) <= 0:
            raise Exception
        ctx.user_data['timetable_settings']["between_range"] = int(msg)
        queries.set_dates_between_range(db_connect(), int(msg))

        keyboard = ReplyKeyboardMarkup(ONLINE_TIMETABLE_SETTINGS, resize_keyboard=True)
        ctx.bot.send_message(chat_id=update.effective_chat.id, text=f"{dates_between_range_has_been_set_msg}\n"
                                                                    f"{timetable_editor_comeback_msg}",
                             reply_markup=keyboard)
        return "online_appointment_settings"
    except Exception as ex:
        print(ex)
        ctx.bot.send_message(chat_id=update.effective_chat.id,
                             text=dates_between_range_tip_msg)
        return "dates_between_range"
