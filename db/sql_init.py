def between_range_table_create(connection, title):
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


def bot_subscribers_table_create(connection, title):
    """table init"""
    with connection.cursor() as cursor:
        try:
            table_create_query = f"CREATE TABLE {title} (" \
                                 "id INT AUTO_INCREMENT," \
                                 "full_name VARCHAR(32) NOT NULL," \
                                 "tg_account VARCHAR(32) NOT NULL," \
                                 "address VARCHAR(255) NOT NULL," \
                                 "phone VARCHAR(32) NOT NULL," \
                                 "chat_id VARCHAR(64) NOT NULL," \
                                 "PRIMARY KEY (id));"
            cursor.execute(table_create_query)
            connection.commit()
            print("table added...")
        except Exception as ex:
            print(ex)


def days_off_table_create(connection, title):
    """table init"""
    with connection.cursor() as cursor:
        try:
            table_create_query = f"CREATE TABLE {title} (" \
                                 "id INT AUTO_INCREMENT," \
                                 "monday INT NOT NULL," \
                                 "tuesday INT NOT NULL," \
                                 "wednesday INT NOT NULL," \
                                 "thursday INT NOT NULL," \
                                 "friday INT NOT NULL," \
                                 "saturday INT NOT NULL," \
                                 "sunday INT NOT NULL," \
                                 "PRIMARY KEY (id));"
            cursor.execute(table_create_query)
            connection.commit()
            print("table added...")
        except Exception as ex:
            print(ex)


def holidays_table_create(connection, title):
    """table init"""
    with connection.cursor() as cursor:
        try:
            table_create_query = f"CREATE TABLE {title} (" \
                                 "id INT AUTO_INCREMENT," \
                                 "begin_date VARCHAR(32) NOT NULL," \
                                 "end_date VARCHAR(32) NOT NULL," \
                                 "PRIMARY KEY (id));"
            cursor.execute(table_create_query)
            connection.commit()
            print("table added...")
        except Exception as ex:
            print(ex)


def invoice_table_create(connection, title):
    """table init"""
    with connection.cursor() as cursor:
        try:
            table_create_query = f"CREATE TABLE {title} (" \
                                 "id INT AUTO_INCREMENT," \
                                 "title VARCHAR(32) NOT NULL," \
                                 "description VARCHAR(255) NOT NULL," \
                                 "long_description VARCHAR(551) NOT NULL," \
                                 "payload VARCHAR(32) NOT NULL," \
                                 "PRIMARY KEY (id));"
            cursor.execute(table_create_query)
            connection.commit()
            print("table added...")
        except Exception as ex:
            print(ex)


def notifies_table_create(connection, title):
    """table init"""
    with connection.cursor() as cursor:
        try:
            table_create_query = f"CREATE TABLE {title} (" \
                                 "id INT AUTO_INCREMENT," \
                                 "mode_id INT NOT NULL," \
                                 "appointment INT NOT NULL," \
                                 "PRIMARY KEY (id));"
            cursor.execute(table_create_query)
            connection.commit()
            print("table added...")
        except Exception as ex:
            print(ex)


def online_dates_table_create(connection, title):
    """table init"""
    with connection.cursor() as cursor:
        try:
            table_create_query = f"CREATE TABLE {title} (" \
                                 "id INT AUTO_INCREMENT," \
                                 "name VARCHAR(32) NOT NULL," \
                                 "date VARCHAR(32) NOT NULL," \
                                 "time VARCHAR(32) NOT NULL," \
                                 "tg_account VARCHAR(32) NOT NULL," \
                                 "chat_id VARCHAR(64) NOT NULL," \
                                 "phone VARCHAR(32) NOT NULL," \
                                 "comment TEXT," \
                                 "PRIMARY KEY (id));"
            cursor.execute(table_create_query)
            connection.commit()
            print("table added...")
        except Exception as ex:
            print(ex)


def price_table_create(connection, title):
    """table init"""
    with connection.cursor() as cursor:
        try:
            table_create_query = f"CREATE TABLE {title} (" \
                                 "id INT AUTO_INCREMENT," \
                                 "title VARCHAR(32) NOT NULL," \
                                 "description TEXT NOT NULL," \
                                 "img BLOB," \
                                 "price INT NOT NULL," \
                                 "PRIMARY KEY (id));"
            cursor.execute(table_create_query)
            connection.commit()
            print("table added...")
        except Exception as ex:
            print(ex)


def replicas_table_create(connection, title):  # unused now
    """table init"""
    with connection.cursor() as cursor:
        try:
            table_create_query = f"CREATE TABLE {title} (" \
                                 "id INT AUTO_INCREMENT," \
                                 "command VARCHAR(45) NOT NULL," \
                                 "replica TEXT NOT NULL," \
                                 "PRIMARY KEY (id));"
            cursor.execute(table_create_query)
            connection.commit()
            print("table added...")
        except Exception as ex:
            print(ex)


def timetable_range_table_create(connection, title):
    """table init"""
    with connection.cursor() as cursor:
        try:
            table_create_query = f"CREATE TABLE {title} (" \
                                 "id INT AUTO_INCREMENT," \
                                 "mode VARCHAR(32) NOT NULL," \
                                 "PRIMARY KEY (id));"
            cursor.execute(table_create_query)
            connection.commit()
            print("table added...")
        except Exception as ex:
            print(ex)


def working_hours_table_create(connection, title):
    """table init"""
    with connection.cursor() as cursor:
        try:
            table_create_query = f"CREATE TABLE {title} (" \
                                 "id INT AUTO_INCREMENT," \
                                 "begin VARCHAR(32) NOT NULL," \
                                 "end VARCHAR(32) NOT NULL," \
                                 "PRIMARY KEY (id));"
            cursor.execute(table_create_query)
            connection.commit()
            print("table added...")
        except Exception as ex:
            print(ex)


def my_test_table_create(connection, title):
    """table init"""
    with connection.cursor() as cursor:
        try:
            table_create_query = f"CREATE TABLE {title} (" \
                                 "id INT AUTO_INCREMENT," \
                                 "begin VARCHAR(32) NOT NULL," \
                                 "dfdf VARCHAR(32) NOT NULL," \
                                 "edging VARCHAR(32) NOT NULL," \
                                 "PRIMARY KEY (id));"
            cursor.execute(table_create_query)
            connection.commit()
            print("table added...")
        except Exception as ex:
            print(ex)


def is_timetable_working_table_create(connection, title):
    """table init"""
    with connection.cursor() as cursor:
        try:
            table_create_query = f"CREATE TABLE {title} (" \
                                 "id INT AUTO_INCREMENT," \
                                 "value VARCHAR(1) NOT NULL," \
                                 "PRIMARY KEY (id));"
            cursor.execute(table_create_query)
            connection.commit()
            print("table added...")
        except Exception as ex:
            print(ex)


def hand_dates_table_create(connection, title):
    with connection.cursor() as cursor:
        try:
            table_create_query = f'CREATE TABLE {title} (' \
                                 f'id INT AUTO_INCREMENT,' \
                                 f'year INT NOT NULL,' \
                                 f'month INT NOT NULL,' \
                                 f'day INT NOT NULL,' \
                                 f'PRIMARY KEY (id));'
            cursor.execute(table_create_query)
            connection.commit()
            print('table added...')
        except Exception as ex:
            print(ex)


def current_dialogues_table_create(connection, title):
    with connection.cursor() as cursor:
        try:
            table_create_query = f'CREATE TABLE {title} (' \
                                 f'id INT AUTO_INCREMENT,' \
                                 f'customer_id VARCHAR(64) NOT NULL,' \
                                 f'admin_id VARCHAR(64) NOT NULL,' \
                                 f'PRIMARY KEY (id));'
            cursor.execute(table_create_query)
            connection.commit()
            print('table added...')
        except Exception as ex:
            print(ex)


def waiting_customers_table_create(connection, title):
    with connection.cursor() as cursor:
        try:
            table_create_query = f"CREATE TABLE {title} (" \
                                 f"id INT AUTO_INCREMENT," \
                                 f"customer_id VARCHAR(64) NOT NULL," \
                                 f"tg_account VARCHAR(32) NOT NULL," \
                                 f"full_name VARCHAR(32) NULL," \
                                 f"message TEXT(512) NULL," \
                                 f"PRIMARY KEY (id));"
            cursor.execute(table_create_query)
            connection.commit()
            print('table added...')
        except Exception as ex:
            print(ex)


def initialize(connection):
    existing_tables = {
        'between_range': between_range_table_create,
        'bot_subscribers': bot_subscribers_table_create,
        'days_off': days_off_table_create,
        'holidays': holidays_table_create,
        'invoice_table': invoice_table_create,
        'notifies': notifies_table_create,
        'online_dates': online_dates_table_create,
        'price': price_table_create,
        'replicas': replicas_table_create,
        'timetable_range': timetable_range_table_create,  # 'testing_table': my_test_table_create,
        'working_hours': working_hours_table_create,
        'is_timetable_working': is_timetable_working_table_create,
        'waiting_customers': waiting_customers_table_create,
        'current_dialogues': current_dialogues_table_create,
        'hand_dates': hand_dates_table_create
    }
    with connection.cursor() as cursor:
        try:
            for table in existing_tables.keys():
                check_query = f"CHECK TABLE `{table}`"
                cursor.execute(check_query)
                result = cursor.fetchone()
                # print(result)  # инфо о данных таблицы
                if result['Msg_text'] != 'OK':
                    existing_tables[table](connection, table)
            print('sql initialized...')
        except Exception as ex:
            print(ex)
