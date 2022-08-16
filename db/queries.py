import logging
import pymysql
from os import environ

from aiogram import Bot, Dispatcher, executor
from aiogram.types import InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils import web_app
from aiogram import types

from context import *

from functions.timetable.new_calendar.constants import weekdays_header_ru


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


def table_create(connection, title):
    """table init"""
    with connection.cursor() as cursor:
        try:
            table_create_query = f"CREATE TABLE {title} (" \
                                 "id INT AUTO_INCREMENT," \
                                 "between_range INT NOT NULL," \
                                 "PRIMARY KEY (id));"
            cursor.execute(table_create_query)
            connection.commit()
            print("table added...")
        except Exception as ex:
            print(ex)


def reset_notifies(connection, when, time, date, chat_id):
    print("restart of notifications..", when, time, date, chat_id)
    from functions.timetable import notifies
    try:
        notifies.schedule_notify(when=when, date=date, time=time, chat_id=chat_id)
    except Exception as ex:
        print(ex)


def set_hand_date(connection, year, month, day):
    with connection.cursor() as cursor:
        query = "INSERT INTO hand_dates (year, month, day) " \
                f"VALUES('{year}', '{month}', '{day}')"
        cursor.execute(query)
        connection.commit()
        print('hand date added')


def delete_hand_date(connection, year, month, day):
    with connection.cursor() as cursor:
        query = f"DELETE FROM hand_dates WHERE year = '{year}' AND month = '{month}' AND day = '{day}'"
        cursor.execute(query)
        connection.commit()
        print("hand date cleared")


def get_hand_date(connection, year, month, day):
    with connection.cursor() as cursor:
        query = f"SELECT * FROM hand_dates WHERE year = '{year}' AND month = '{month}' AND day = '{day}'"
        cursor.execute(query)
        data = cursor.fetchone()
        return data


def get_hand_dates(connection):
    with connection.cursor() as cursor:
        query = f"SELECT * FROM hand_dates"
        cursor.execute(query)
        data = cursor.fetchall()
        return data


def get_data(connection):
    with connection.cursor() as cursor:  # Поработать над форматом вывода информации о клиентах, чтобы было красиво.
        get_data_query = "SELECT * FROM online_dates"
        cursor.execute(get_data_query)
        rows = cursor.fetchall()
        rows = list(sorted(rows, key=lambda x: (
            int(x['date'].split("-")[-1]),
            int(x['date'].split("-")[-2]),
            int(x['date'].split("-")[-3]),
            int(x['time'].split(":")[-2]),
            int(x['time'].split(":")[-1]))))
        count = len(rows)
        return [count, rows]


def get_busy_dates(connection):
    rows = get_data(connection)[-1]
    dates = []
    if not len(rows):
        return None
    for row in rows:
        day, month, year = map(int, row['date'].split("-"))
        time = row['time']
        dates.append([year, month, day, time])
    return dates


def add_service_to_price(connection, title, price, description=None, img=None):
    with connection.cursor() as cursor:
        if description is None:
            description = "-"
        if img is None:
            add_query = "INSERT INTO `price` (title,description,price)" \
                        f"VALUES('{title}', '{description}', '{price}')"
        elif img is not None:
            add_query = "INSERT INTO `price` (title,description,price,img)" \
                        f"VALUES('{title}', '{description}', '{price}', '{img}')"
        cursor.execute(add_query)
        connection.commit()
        print("new service has been added.")


def get_service_from_price(connection):
    with connection.cursor() as cursor:
        get_query = "SELECT * FROM `price`"
        cursor.execute(get_query)
        all_the_services = cursor.fetchall()
        return all_the_services


def delete_service_from_price(connection, title):
    with connection.cursor() as cursor:
        del_query = f"DELETE FROM `price` WHERE `title` = '{title}'"
        cursor.execute(del_query)
        connection.commit()
        print(f"{title} has been delete from the check_list.")


def get_working_hours(connection):
    with connection.cursor() as cursor:
        get_working_hours_query = f"SELECT * FROM working_hours"
        cursor.execute(get_working_hours_query)
        working_hours = cursor.fetchone()
        if working_hours is None:
            working_time_adding(connection, begin_time="08:00", end_time='21:00')
            return get_working_hours(connection)
        return working_hours


def get_user_last_date(connection, chat_id):
    with connection.cursor() as cursor:
        get_users_query = f"SELECT * FROM online_dates WHERE `chat_id` = '{chat_id}'"
        cursor.execute(get_users_query)
        last_date = cursor.fetchone()
        return last_date


def working_time_adding(connection, begin_time, end_time):
    with connection.cursor() as cursor:
        clear_query = "DELETE FROM `working_hours` WHERE id"
        cursor.execute(clear_query)
        adding_query = f"INSERT INTO `working_hours` (begin, end)" \
                       f" VALUES ('{begin_time}', '{end_time}');"
        cursor.execute(adding_query)
        connection.commit()
        print("new working time has been set...")


def set_timetable_range(connection, mode):
    with connection.cursor() as cursor:
        clear_query = "DELETE FROM `timetable_range` WHERE id"
        cursor.execute(clear_query)
        set_query = f"INSERT INTO `timetable_range` (mode)" \
                    f" VALUES('{mode}');"
        try:
            cursor.execute(set_query)
        except Exception as ex:
            print(ex)
        connection.commit()
        print("new timetable_range has been set...")


def get_timetable_range(connection):
    with connection.cursor() as cursor:
        query = "SELECT * FROM `timetable_range`"
        cursor.execute(query)
        timetable_range = cursor.fetchone()
        if timetable_range is None:
            mode = 90
            set_timetable_range(connection, mode=mode)
            return mode
        return int(timetable_range["mode"])


def set_phone_number(connection, phone):
    with connection.cursor() as cursor:
        query = f"INSERT INTO `bot_subscribers` (phone) VALUES('{phone}');"
        cursor.execute(query)
        connection.commit()


def get_sub_chats(connection):
    with connection.cursor() as cursor:
        query = "SELECT * FROM `bot_subscribers`"
        cursor.execute(query)
        subs = cursor.fetchall()
        return subs


def get_notifies(connection):
    with connection.cursor() as cursor:
        query = "SELECT * FROM `notifies`"
        cursor.execute(query)
        notifies_data = cursor.fetchone()
        return notifies_data


def set_notifies(connection, mode_id, chat_id):
    with connection.cursor() as cursor:
        query = "INSERT INTO `notifies` (mode_id, appointment_id)" \
                f"VALUES('{mode_id}', '{chat_id}');"
        cursor.execute(query)
        connection.commit()


def set_days_off(connection, day):
    with connection.cursor() as cursor:
        choose_all_query = "SELECT * FROM `days_off`"
        cursor.execute(choose_all_query)
        all_the_weekdays = cursor.fetchall()
        if not all_the_weekdays:
            all_the_weekdays = {
                "ПН": False,
                "ВТ": False,
                "СР": False,
                "ЧТ": False,
                "ПТ": False,
                "СБ": False,
                "ВС": False
            }
            all_the_weekdays[day] = not all_the_weekdays[day]
            values = list()
            for i in all_the_weekdays.values():
                values.append(1) if i else values.append(0)
        else:
            abbr_to_month = {
                "ПН": "monday",
                "ВТ": "tuesday",
                "СР": "wednesday",
                "ЧТ": "thursday",
                "ПТ": "friday",
                "СБ": "saturday",
                "ВС": "sunday"
            }
            all_the_weekdays[0][abbr_to_month[day]] = 1 if int(all_the_weekdays[0][abbr_to_month[day]]) == 0 else 0
            values = []
            for i in list(all_the_weekdays[0].values())[1:]:
                values.append(1) if i else values.append(0)
            clear_query = "DELETE FROM `days_off` WHERE id"
            cursor.execute(clear_query)

        adding_query = "INSERT INTO `days_off` (monday, tuesday, wednesday, thursday, friday, saturday, sunday) " \
                       f"VALUES ('{values[0]}', '{values[1]}', '{values[2]}', '{values[3]}', '{values[4]}', " \
                       f"'{values[5]}', '{values[6]}');"
        cursor.execute(adding_query)
        connection.commit()
        return values


def get_days_off(connection):
    with connection.cursor() as cursor:
        query = "SELECT * FROM `days_off`"
        cursor.execute(query)
        values = cursor.fetchone()
        if values is None:
            set_days_off(connection, day='ПН')
            return get_days_off(connection)
        values = list(values.values())[1:]
        days_off = [weekdays_header_ru[i] for i in range(len(weekdays_header_ru)) if values[i] == 1]
        return days_off


def set_holidays(connection, first_date, second_date):
    with connection.cursor() as cursor:
        clear_query = "DELETE FROM `holidays` WHERE id"
        cursor.execute(clear_query)
        query = "INSERT INTO `holidays` (begin_date, end_date) VALUES " \
                f"('{first_date}', '{second_date}');"
        cursor.execute(query)
        connection.commit()
        print("new holidays have been set..")


def switch_timetable_working(connection):
    with connection.cursor() as cursor:
        query = 'SELECT * FROM `is_timetable_working`'
        cursor.execute(query)
        try:
            value = int(cursor.fetchone()['value'])
        except Exception as ex:
            print(ex)
            set_query = f"INSERT INTO `is_timetable_working` (value) VALUE('1'); "
            cursor.execute(set_query)
            connection.commit()
            print("value has been initialized..")
            return
        # clearing:
        clear_query = 'DELETE FROM `is_timetable_working` WHERE id'
        cursor.execute(clear_query)
        connection.commit()
        # new value setting:
        if value == 1:
            set_query = f"INSERT INTO `is_timetable_working` (value)" \
                        f" VALUES('0');"
        else:
            set_query = f"INSERT INTO `is_timetable_working` (value)" \
                        f" VALUES('1');"
        cursor.execute(set_query)
        connection.commit()
        print("timetable_working switched.")
        return True if value == 0 else False


def get_is_timetable_working(connection):
    with connection.cursor() as cursor:
        get_query = 'SELECT * FROM `is_timetable_working`'
        cursor.execute(get_query)
        try:
            result = cursor.fetchone()['value']
        except Exception as ex:
            print(ex)
            # set_is_timetable_working function:
            set_query = f"INSERT INTO `is_timetable_working` (value)" \
                        f" VALUE('1'); "
            cursor.execute(set_query)
            connection.commit()
            print("value has been initialized..")
            get_is_timetable_working(connection)
        return True if result == "1" else False


def get_holidays(connection):
    with connection.cursor() as cursor:
        query = "SELECT * FROM `holidays`"
        cursor.execute(query)
        current_holidays = cursor.fetchone()
        return current_holidays


def get_dates_between_range(connection):
    with connection.cursor() as cursor:
        query = "SELECT * FROM `between_range`"
        cursor.execute(query)
        current_range = cursor.fetchone()
        if current_range is None:
            mode = 30  # appointments duration (min)
            insert_query = f"INSERT INTO `between_range` (between_range)" \
                           f" VALUES ('{mode}');"
            cursor.execute(insert_query)
            connection.commit()
            return mode
        return int(current_range["between_range"])


def set_dates_between_range(connection, data):
    with connection.cursor() as cursor:
        clear_query = "DELETE FROM `between_range` WHERE id"
        cursor.execute(clear_query)
        query = "INSERT INTO `between_range` (between_range) VALUES " \
                f"('{data}');"
        cursor.execute(query)
        connection.commit()
        print("new between_range have been set..")


def cancel_holidays(connection):
    with connection.cursor() as cursor:
        check_query = "SELECT * FROM `holidays`"
        cursor.execute(check_query)
        check = cursor.fetchone()
        if check is None:
            return None
        clear_query = "DELETE FROM `holidays` WHERE id"
        cursor.execute(clear_query)
        connection.commit()
        print("holidays have been canceled.")
        return check


def clear_holidays(connection, date):
    with connection.cursor() as cursor:
        query = f"DELETE FROM `holidays` WHERE end_date = '{date}'"
        cursor.execute(query)
        connection.commit()
        print('holidays cleared..')


def is_authorized(connection, chat_id):
    """ does the user exist in db? """
    with connection.cursor() as cursor:
        check_query = f"SELECT * FROM `bot_subscribers` WHERE `chat_id` = '{chat_id}'"
        cursor.execute(check_query)
        result = cursor.fetchone()
        if result is None:
            return False
        return True


def make_an_appointment(connection, full_name, date, time, tg_account, chat_id, comment):
    """appointment making"""
    with connection.cursor() as cursor:
        appointment_add_query = "INSERT INTO online_dates (name, date, time, tg_account, chat_id, comment)" \
                                f" VALUES ('{full_name}', '{date}'," \
                                f" '{time}', '{tg_account}', '{chat_id}', '{comment}');"
        cursor.execute(appointment_add_query)
        connection.commit()
        print("appointment added...")


def new_user_adding(connection, full_name, tg_account, chat_id):
    """ user registration into db"""
    with connection.cursor() as cursor:
        user_add_query = f"INSERT INTO bot_subscribers (full_name, tg_account, chat_id)" \
                         f" VALUES ('{full_name}', '{tg_account}', '{int(chat_id)}');"
        cursor.execute(user_add_query)
        connection.commit()
        print("new user added...")


def create_new_dialogue(connection, admin_id, customer_id):
    with connection.cursor() as cursor:
        create_query = 'INSERT INTO current_dialogues (admin_id, customer_id)' \
                       f" VALUES('{admin_id}', '{customer_id}');"
        cursor.execute(create_query)
        connection.commit()
        print("dialogue created...")


def delete_dialogue(connection, admin_id=None, customer_id=None):
    try:
        with connection.cursor() as cursor:
            if admin_id is None and customer_id is None:
                raise Exception("Both arguments (admin and chat ids) couldn't be none-type.")
            if admin_id is None:
                query = f"DELETE FROM current_dialogues WHERE customer_id = '{customer_id}'"
            elif customer_id is None:
                query = f"DELETE FROM current_dialogues WHERE admin_id = '{admin_id}'"
            cursor.execute(query)
            connection.commit()
            print("dialogue was deleted..")
    except Exception as ex:
        print(ex)


def get_dialogues(connection, customer_id=None):
    with connection.cursor() as cursor:
        query = 'SELECT * FROM current_dialogues'
        if customer_id is not None:
            query = f"SELECT * FROM current_dialogues WHERE customer_id = '{customer_id}'"
        cursor.execute(query)
        data = cursor.fetchall()
        return data


def add_waiting_customer(connection, customer_id, tg_account, full_name, message=None):
    with connection.cursor() as cursor:
        add_query = f'INSERT INTO waiting_customers (customer_id, tg_account, full_name) ' \
                    f"VALUES('{customer_id}', '{tg_account}', '{full_name}');"
        cursor.execute(add_query)
        connection.commit()
        print("waiting_customer added..")


def delete_waiting_customer(connection, customer_id):
    with connection.cursor() as cursor:
        delete_query = f"DELETE FROM waiting_customers WHERE customer_id = '{customer_id}'"
        cursor.execute(delete_query)
        connection.commit()
        print('waiting_customer deleted..')


def get_waiting_customers(connection):
    """ customers that are waiting support"""
    with connection.cursor() as cursor:
        get_query = "SELECT * FROM waiting_customers"
        cursor.execute(get_query)
        data = cursor.fetchall()
        print(data)
        return data


def clear_subscribers(connection):  # USE WITH ATTENTION!
    """ clear all the bot_subscribers """
    with connection.cursor() as cursor:
        clear_query = "DELETE FROM `bot_subscribers` WHERE (id)"
        cursor.execute(clear_query)
        connection.commit()
        print("bot_subscribers cleared")


def delete_appointment(connection, chat_id):
    with connection.cursor() as cursor:
        try:
            delete_query = f"DELETE FROM `online_dates` " \
                           f"WHERE (`chat_id` = '{chat_id}');"
            cursor.execute(delete_query)
            connection.commit()
        except Exception as ex:
            print(ex)


def clear_appointments(connection):
    with connection.cursor() as cursor:
        clear_query = "DELETE FROM `online_dates` WHERE id"
        cursor.execute(clear_query)
        connection.commit()


def clear_appointment(connection, info):
    time, date = [i for i in info]
    with connection.cursor() as cursor:
        clear_query = f"DELETE FROM `online_dates` WHERE time = '{time}' AND date = '{date}'"
        cursor.execute(clear_query)
        connection.commit()
        print(f"The appointment from {date}, {time} was cleared from database.")

# # place for query tests: (не удалять)
#
#
# from functions.timetable.tools import db_connect
#
# from os import environ, path
# from dotenv import load_dotenv
#
# if path.exists('../../.env'):  # Переменные окружения хранятся в основной директории проекта
#     load_dotenv('../../.env')
# else:
#     raise ImportError("Can't import environment variables")
# connection = db_connect()
