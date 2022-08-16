from dateutil.tz import gettz
from telegram.ext import Updater
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

from base_template.db import queries
from base_template.keyboards import ONLINE_TIMETABLE_user_menu
from functions.timetable.tools import *
import datetime as dt
from .objects import *
from os import environ
from .constants import *
import calendar

TIMEZONE = gettz('Asia/Yekaterinburg')


def calendar_gen(update, ctx, do_calendar_settings=False, days_off=None, holidays=None, working_hours=None,
                 between_range=datetime.timedelta(minutes=30), timetable_range=None, test=False, hand_dates=None,
                 return_handler=None):
    """ modified calendar generator """
    if working_hours is None:
        working_hours = ctx.user_data['timetable_settings']['working_hours']
    if days_off is None:
        days_off = ctx.user_data['timetable_settings']['days_off']
    if hand_dates is None:
        hand_dates = ctx.user_data['timetable_settings']['hand_dates']
    if holidays is None:
        holidays = ctx.user_data['timetable_settings']['holidays']
    if timetable_range is None:  # range opportunity to make appointment (month/3 month/year)
        timetable_range = ctx.user_data['timetable_settings']['timetable_range']
    all_the_dates = [Year((datetime.datetime.now() + TIME_SHIFT).year)]  # можно добавлять года аналогичным способом.
    busy_dates = get_busy_dates(db_connect())
    for year in all_the_dates:
        for month in range(1, 13):
            days_in_month = int(calendar.monthrange(year.year, month)[-1])
            cur_month = Month(month, days_count=days_in_month)
            year.months.append(cur_month)
            for day in range(1, days_in_month + 1):
                cur_day = Day(day)
                week_day = datetime.datetime(year=year.year, month=month, day=day).weekday()
                year.months[-1].days.append(cur_day)

                # time formatting:
                begin_time_str = working_hours['begin']
                begin_time = datetime.timedelta(hours=int(begin_time_str.split(":")[0]),
                                                minutes=int(begin_time_str.split(":")[1]))
                end_time_str = working_hours['end']
                end_time = datetime.timedelta(hours=int(end_time_str.split(":")[0]),
                                              minutes=int(end_time_str.split(":")[1]))
                time = begin_time

                hours, minutes = int(begin_time_str.split(":")[0]), int(begin_time_str.split(":")[1])
                while time <= end_time:
                    cur_time = Time(hours, minutes)
                    now_dt = datetime.datetime.now() + TIME_SHIFT
                    cur_dt = datetime.datetime(year=year.year, month=cur_month.month, day=cur_day.day,
                                               hour=hours, minute=minutes)
                    if do_calendar_settings:
                        # --reformatting holidays data:
                        if holidays is not None:
                            holidays_begin_date = holidays['begin_date'].split('-')
                            holidays_end_date = holidays['end_date'].split('-')
                            holidays_begin_date = datetime.datetime(year=int(holidays_begin_date[0]),
                                                                    month=int(holidays_begin_date[1]),
                                                                    day=int(holidays_begin_date[2]))
                            holidays_end_date = datetime.datetime(year=int(holidays_end_date[0]),
                                                                  month=int(holidays_end_date[1]),
                                                                  day=int(holidays_end_date[2])) + dt.timedelta(days=1)
                            if holidays_begin_date <= cur_dt <= holidays_end_date:  # не явл. ли отпуском
                                cur_time.available = False

                        range_dt = now_dt + datetime.timedelta(days=timetable_range)
                        postponement = datetime.timedelta(hours=0)  # Отсрочка записи от настоящего времени
                        if not (range_dt >= cur_dt > now_dt + postponement):  # попадает ли в timetable_range
                            cur_time.available = False

                        # days_off check:
                        if days_off is not None:
                            days_off_indexes = ExceptionCog().get_days_off_indexes(days_off)
                            if week_day in days_off_indexes:
                                cur_time.available = False

                        # busy time checking:
                        if busy_dates is not None:
                            if [int(year.year), int(month), int(day), cur_time.str_time] in busy_dates:
                                cur_time.available = False

                    year.months[-1].days[-1].time.append(cur_time)
                    time = time + between_range

                    total_seconds = int(time.total_seconds())
                    hours, remainder = divmod(total_seconds, 60 * 60)
                    minutes, seconds = divmod(remainder, 60)

                if hand_dates is not None:
                    for hand_date in hand_dates:
                        if hand_date['year'] == year.year and \
                                hand_date['month'] == month and hand_date['day'] == day:
                            cur_day.available = False
                            cur_day.hand_date = True
                # Реализация рекурсивной проверки дат (плесневелая пока что, надо обойтись более линейным способом):
                if not any([i.available for i in cur_day.time]):  # если на дню нет свобод. времени, день занят.
                    cur_day.available = False
            if not any([i.available for i in cur_month.days]):  # нет дней - месяц занят, на год делать абсурд
                cur_month.available = False
    # test ending:
    ctx.user_data['my_all_the_dates'] = all_the_dates
    if test:
        return
    print("calendar generated.")
    # print('год:', all_the_dates[0],
    #       'месяца:', '; '.join([f"{m.month}, {m.available}" for m in all_the_dates[0].months]),
    #       'дни:', '; '.join([f"{d.day}, {d.available}" for d in all_the_dates[0].months[2].days]),
    #       'время:', '; '.join([f"{t.time}, {t.available}" for t in all_the_dates[0].months[2].days[18].time]),
    #       sep='\n')
    # Предложение выбора месяца:
    ctx.bot.send_message(chat_id=update.effective_chat.id, text='📆', reply_markup=ReplyKeyboardRemove())
    ctx.bot.send_message(chat_id=update.effective_chat.id,
                         text=choose_the_month,
                         reply_markup=get_months_nav(update, ctx))
    # get_months_nav(update, ctx)  # выбор месяцев.
    # get_days_keys2(update, ctx)
    if return_handler is None:
        return 'time_choosing2'
    else:
        return return_handler


def get_time_keys(update, ctx, all_times=None):
    if all_times is None:
        year = int(ctx.user_data['date_of_appointment']['year'])
        month = int(ctx.user_data['date_of_appointment']['month'])
        day = int(ctx.user_data['date_of_appointment']['day'])
        all_times = [':'.join(list(map(str, i.time))) for i in
                     ctx.user_data['my_all_the_dates'][0].months[month - 1].days[day - 1].time
                     if i.available]
        # TEST below:
        for i in range(len(all_times)):
            new_row = list(all_times[i])
            if len(all_times[i].split(":")[0]) != 2:
                new_row.insert(0, '0')
                all_times[i] = ''.join(new_row)
            if len(all_times[i].split(":")[1]) != 2:
                new_row.insert(-1, '0')
                all_times[i] = ''.join(new_row)
    keys = [[i] for i in all_times]
    keys.insert(0, [change_date_btn])
    keyboard = ReplyKeyboardMarkup(keys, resize_keyboard=True)
    return keyboard


def get_months_nav(update, ctx, all_dates=None):
    if all_dates is None:
        all_dates = ctx.user_data['my_all_the_dates']
    months = all_dates[0].months
    rows = InlineKeyboardMarkup([])
    row = []
    for month in months:
        if month.available:
            row.append(InlineKeyboardButton(month_abbr_ru[month.month], callback_data='month_choosing|' +
                                                                                      str(month.month)))
        if len(row) % 3 == 0:
            rows.inline_keyboard.append(row[:])
            row.clear()
    if len(row) > 0:
        rows.inline_keyboard.append(row[:])
        row.clear()
    # ctx.bot.send_message(chat_id=update.effective_chat.id,
    #                      text=choose_the_month,
    #                      reply_markup=rows)
    if ctx.user_data['hand_date_choose']:
        rows.inline_keyboard.append([InlineKeyboardButton(back_btn, callback_data='calendar_back')])
    return rows


def get_days_keys2(update, ctx, month_num=datetime.date.today().month, all_dates=None):
    if all_dates is None:
        all_dates = ctx.user_data["my_all_the_dates"]
    days = all_dates[0].months[month_num - 1].days
    rows = InlineKeyboardMarkup([])
    rows.inline_keyboard.append(
        [InlineKeyboardButton(i, callback_data="pass") for i in weekdays_header_ru])  # header adding..
    row = []
    num = 1
    btn_num = 0
    first_weekday = calendar.monthrange(all_dates[0].year, month_num)[0]
    while num <= len(days):
        for i in range(7):
            btn_num += 1
            if btn_num <= first_weekday or num > len(days):
                row.append(InlineKeyboardButton(" ", callback_data="pass"))
                continue
            elif days[num - 1].hand_date and ctx.user_data['hand_date_choose']:
                row.append(InlineKeyboardButton("🚫", callback_data='day_choosing|' + str(num)))
                num += 1
                continue
            elif not days[num - 1].available:
                row.append(InlineKeyboardButton(" ", callback_data='pass'))
                num += 1
                continue
            row.append(InlineKeyboardButton(str(num), callback_data='day_choosing|' + str(num)))
            num += 1
        rows.inline_keyboard.append(row[:])
        row.clear()
    # ctx.bot.send_message(chat_id=update.effective_chat.id,
    #                      text=choose_the_day,
    #                      reply_markup=rows)
    # navigation buttons:
    manage_buttons = [InlineKeyboardButton('<<', callback_data='day_choosing|' + '<<'),
                      InlineKeyboardButton(month_abbr_ru[month_num], callback_data='day_choosing|' + 'month_re-elect'),
                      InlineKeyboardButton('>>', callback_data='day_choosing|' + '>>')]
    rows.inline_keyboard.append(manage_buttons)
    return rows


def calendar_build(update, ctx, entry_state="month", do_timetable_settings=False):
    """ calendar with settings opportunities configuration """
    # do_timetable_settings - accept admin settings or no
    # user_data init:
    ctx.user_data["date_of_appointment"] = {'year': None, 'month': None, 'day': None, "time": None}
    ctx.user_data["is_date_choice"] = False

    if entry_state == "month":
        month_keys = get_month_keys(do_timetable_settings, timetable_settings=ctx.user_data["timetable_settings"])
        keyboard = InlineKeyboardMarkup(month_keys)
        ctx.bot.send_message(chat_id=update.effective_chat.id,
                             text="Выберите месяц:",
                             reply_markup=keyboard)
    elif entry_state == "day":
        month = (dt.datetime.now() + TIME_SHIFT).month
        year = CalendarCog().get_year(int(month))
        ctx.user_data["date_of_appointment"]['year'] = year
        ctx.user_data["date_of_appointment"]['month'] = month
        days_keys = get_days_keys(year, month,
                                  do_timetable_settings=ctx.user_data["make_an_appointment"],
                                  timetable_settings=ctx.user_data["timetable_settings"])
        keyboard = InlineKeyboardMarkup(days_keys)
        ctx.bot.send_message(chat_id=update.effective_chat.id,
                             text=f"Выберите день (календарь на {month_name_ru[month - 1]}):",
                             reply_markup=keyboard)

    elif entry_state == "year":
        pass
    ctx.user_data["is_date_choice"] = True
    return "time_choosing"


def get_month_keys(do_timetable_settings, timetable_settings=None):
    """ getting month keys (winter, spring, summer, autumn) """
    if do_timetable_settings:
        month_range = list(
            map(lambda x: x.month, ExceptionCog().get_timetable_range(timetable_settings["timetable_range"])))
        start = month_range[0]
        end = month_range[1]
        correctly_month_values = set()
        correctly_month_values.add(end)

        if start == end:
            for i in range(1, 13):
                correctly_month_values.add(i)
        elif start < end:
            for i in range(start, end + 1):
                correctly_month_values.add(i)
        elif start > end:
            for i in range(1, 13):
                if i <= end or i >= start:
                    correctly_month_values.add(i)
        month_range = correctly_month_values

        # ниже попытки решить проблему с отпуском на несколько месяцев
        holidays_range = list(ExceptionCog().get_holidays_range(queries.get_holidays(db_connect())))
        holidays_days = (holidays_range[-1] - holidays_range[0]).days
        holidays_range = [holidays_range[0] + relativedelta(days=i) for i in range(0, holidays_days + 1)]

    rows = []
    row = []
    for i in range(1, 12 + 1):
        shifting = i - 1
        if shifting == 0:
            shifting = 12
        start_month_date = datetime.date((datetime.datetime.now() + TIME_SHIFT).year, shifting, 1)
        end_month_date = datetime.date((datetime.datetime.now() + TIME_SHIFT).year, shifting,
                                       1) + relativedelta(
            months=1) - relativedelta(days=1)
        days_in_month_count = end_month_date.day
        month_dates = [datetime.date((datetime.datetime.now() + TIME_SHIFT).year, shifting, i)
                       for i in range(1, days_in_month_count)]

        if do_timetable_settings and shifting in month_range:
            row.append(month_abbr_ru[shifting])
        elif not do_timetable_settings:
            row.append(month_abbr_ru[shifting])
        if i % 3 == 0:  # разбиение на строки по сезонам (выглядит хорошо только когда 12 из 12 мес)
            rows.append([InlineKeyboardButton(x, callback_data=month_ru.index(x) + 1) for x in row])
            row.clear()
    return rows


def get_slider_keys(month=None, year=None):
    if month:
        return ["<<", month_abbr_ru[month], ">>"]
    elif year:
        return


def get_days_keys(year, months_num, do_timetable_settings=False, timetable_settings=None):
    """ getting weekdays keys """
    first_weekday, month_range = calendar.monthrange(year, months_num)
    if do_timetable_settings:
        timetable_range = ExceptionCog().get_timetable_range(timetable_settings["timetable_range"])
        days_off = ExceptionCog().get_days_off_indexes(timetable_settings["days_off"])
        holidays_range = ExceptionCog().get_holidays_range(timetable_settings["holidays"])

    rows = list()
    rows.append([InlineKeyboardButton(i, callback_data="pass") for i in weekdays_header_ru])  # header adding..
    row = []
    num = 1
    btn_num = 0
    while num <= month_range:
        for i in range(7):
            btn_num += 1
            if btn_num <= first_weekday or num > month_range:
                row.append(InlineKeyboardButton(" ", callback_data="pass"))
                continue
            if do_timetable_settings:
                iter_date = datetime.date(year=year, month=months_num, day=num)
                if timetable_range[0] <= iter_date <= timetable_range[-1] and \
                        i not in days_off and \
                        (holidays_range is None or not holidays_range[0] <= iter_date <= holidays_range[-1]):
                    row.append(InlineKeyboardButton(str(num), callback_data=num))
                else:
                    row.append(InlineKeyboardButton(" ", callback_data="pass"))
            else:
                row.append(InlineKeyboardButton(str(num), callback_data=num))
            num += 1
        rows.append(row[:])
        row.clear()
    return rows


def main() -> None:
    updater = Updater(token=environ.get("BOT_TOKEN"), use_context=True)
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
