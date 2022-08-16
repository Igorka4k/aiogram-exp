import pymysql
import datetime
from dateutil.relativedelta import relativedelta
from dateutil.tz import gettz

from base_template.db.queries import *
from .new_calendar.constants import *
from base_template.context import *
from os import environ

TIMEZONE = gettz('Asia/Yekaterinburg')
TIME_SHIFT = datetime.timedelta(hours=5)


def db_connect():
    try:
        connection = pymysql.connect(
            host=environ.get('MYSQL_URL'),
            port=int(environ.get('MYSQL_PORT')),
            password=environ.get('MYSQL_PASS'),
            database=environ.get('MYSQL_BASE_NAME'),
            user=environ.get('MYSQL_USER'),
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as ex:
        print("connection refused.")
        print(ex)
        return False


def get_datetime_from_formatting(formatting_date):
    day, month, year = map(int, formatting_date.split(",")[0].split("-"))
    hour, minute = map(int, formatting_date.split(",")[1].split(":"))
    return datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute)


def get_timedelta(date):
    return date - (datetime.datetime.utcnow() + TIME_SHIFT)


class CalendarCog:
    def __init__(self):
        pass

    def get_year(self, choice_month: int):
        if (datetime.datetime.utcnow() + TIME_SHIFT).month > choice_month:
            return datetime.datetime.now().year + 1
        return datetime.datetime.now().year

    def get_days_keyboard(self, year, month):
        d1 = datetime.date(year, month, 1)
        d2 = datetime.date(year, month + 1, 1)
        days_keyboard = [[str((d1 + datetime.timedelta(days=x)).day)] for x in range((d2 - d1).days)]
        return days_keyboard

    def chosen_date_formatting(self, date):
        date['month'] = "0" + str(date['month']) if len(str(date["month"])) == 1 else str(date['month'])
        date['day'] = "0" + str(date['day']) if len(str(date["day"])) == 1 else str(date['day'])
        formatted_date = f"{date['year']}-{date['month']}-{date['day']}"
        return formatted_date

    def get_hours_keyboard(self, begin=None, end=None, between_range=None):
        if begin and end:
            begin = datetime.time(int(begin.split(":")[0]), int(begin.split(":")[1]))
            end = datetime.time(int(end.split(":")[0]), int(end.split(":")[1]))
        hours_keyboard = []
        if begin > end:
            ans = self.get_hours_keyboard(begin='00:00', end=end.strftime('%H:%M'), between_range=between_range)
            ans.extend(self.get_hours_keyboard(begin=begin.strftime('%H:%M'), end="23:59", between_range=between_range))
            return ans
        iter_time = begin
        if between_range is None:
            between_range = 10  # Диапазон между записями.
        while iter_time <= end:
            hours_keyboard.append([iter_time.strftime("%H:%M")])
            timedelta = datetime.timedelta(hours=iter_time.hour, minutes=iter_time.minute) \
                        + datetime.timedelta(minutes=between_range)
            total_seconds = int(timedelta.total_seconds())
            hours, remainder = divmod(total_seconds, 60 * 60)
            minutes, seconds = divmod(remainder, 60)
            if hours >= 24:
                break
            iter_time = datetime.time(hour=hours, minute=minutes, second=seconds)

        # # для изменения диапазона между записями надо изменить (1) и (2)
        # one_hour = datetime.timedelta(minutes=0)
        # for i in range(0, 24 * 2):  # (1)
        #     total_seconds = int(one_hour.total_seconds())
        #     hours, remainder = divmod(total_seconds, 60 * 60)
        #     minutes, seconds = divmod(remainder, 60)
        #     iter_time = datetime.time(hours, minutes, 0)
        #     if begin is not None and end is not None:
        #         if begin <= iter_time <= end:
        #             hours_keyboard.append([iter_time.strftime("%H:%M")])
        #     else:
        #         hours_keyboard.append([iter_time.strftime("%H:%M")])
        #     one_hour = one_hour + datetime.timedelta(minutes=30)  # (2)
        return hours_keyboard

    def count_days_in_year(self, n):
        if n % 4 != 0:
            return 365
        if n % 100 != 0:
            return 366
        if n % 400 != 0:
            return 365
        return 366


class ExceptionCog:
    def __init__(self):
        pass

    def get_timetable_range(self, timetable_range):
        range_itself = datetime.date.today() + relativedelta(days=timetable_range)
        return [datetime.date.today() + relativedelta(days=1), range_itself]

    def get_days_off_indexes(self, the_days_off):
        if the_days_off is None:
            return []
        days_off_indexes = []

        for i in range(7):
            if weekdays_header_ru[i] in the_days_off:
                days_off_indexes.append(i)
        return days_off_indexes

    def get_holidays_range(self, holidays):
        if holidays is None:
            return None
        begin_date = list(map(int, holidays["begin_date"].split("-")))
        begin_date = datetime.date(year=begin_date[0], month=begin_date[1], day=begin_date[2])
        end_date = list(map(int, holidays["end_date"].split("-")))
        end_date = datetime.date(year=end_date[0], month=end_date[1], day=end_date[2])
        return [begin_date, end_date]
