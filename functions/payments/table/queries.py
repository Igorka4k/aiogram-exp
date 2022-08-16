import pymysql
from os import environ, path

# from dotenv import load_dotenv
#
# if path.exists('../../../.env'):  # Переменные окружения хранятся в основной директории проекта
#     load_dotenv('../../../.env')
# else:
#     raise ImportError("Can't import environment variables")


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
        # print("successfully connected...")
        return connection
    except Exception as ex:
        print("connection refused.")
        print(ex)
        return False


def payment_table_create(connection):
    with connection.cursor() as cursor:
        try:
            table_create_query = f"CREATE TABLE `invoice_table` (" \
                                 "`id` int auto_increment," \
                                 "`title` varchar(32) NOT NULL," \
                                 "`description` varchar(255) NOT NULL," \
                                 "`long_description` varchar(511) NOT NULL," \
                                 "`payload` varchar(32) NOT NULL," \
                                 "`price` int NOT NULL," \
                                 "PRIMARY KEY  (`id`));"
            cursor.execute(table_create_query)
            connection.commit()
            print(f"invoice_table table added...")
        except Exception as ex:
            print(ex)


def add_invoice(connection, title: str, description: str, payload: str, price: int):
    try:
        with connection.cursor() as cursor:
            add_query = "INSERT INTO invoice_table (title, description, long_description, payload, price)" \
                        f" VALUES ('{title}', '{description}'," \
                        f" '{description}', '{payload}', {price});"
            cursor.execute(add_query)
            connection.commit()
            # print("invoice added...")
    except pymysql.err.ProgrammingError:
        payment_table_create(connection)
        with connection.cursor() as cursor:
            add_query = "INSERT INTO invoice_table (title, description, long_description, payload, price)" \
                        f" VALUES ('{title}', '{description}'," \
                        f" '{description}', '{payload}', {price});"
            cursor.execute(add_query)
            connection.commit()
            # print("invoice added...")


def remove_invoice(connection, title: str):
    try:
        with connection.cursor() as cursor:
            add_query = f"DELETE FROM invoice_table WHERE title='{title}';"
            cursor.execute(add_query)
            connection.commit()
            # print("invoice removed...")
    except pymysql.err.ProgrammingError:
        payment_table_create(connection)
        with connection.cursor() as cursor:
            add_query = f"DELETE FROM invoice_table WHERE title='{title}';"
            cursor.execute(add_query)
            connection.commit()
            # print("invoice removed...")


def get_data(connection):
    try:
        with connection.cursor() as cursor:
            add_query = f"SELECT * FROM invoice_table;"
            cursor.execute(add_query)
            connection.commit()
            # print("data got...")
            result = cursor.fetchall()
            return result
    except pymysql.err.ProgrammingError:
        payment_table_create(connection)
        with connection.cursor() as cursor:
            add_query = f"SELECT * FROM invoice_table;"
            cursor.execute(add_query)
            connection.commit()
            # print("data got...")
            result = cursor.fetchall()
            return result


def get_invoice(connection, id_: int):
    try:
        with connection.cursor() as cursor:
            add_query = f"SELECT * FROM invoice_table WHERE id={id_};"
            cursor.execute(add_query)
            connection.commit()
            print("invoice got...")
            result = cursor.fetchone()
            return result
    except pymysql.err.ProgrammingError:
        payment_table_create(connection)
        with connection.cursor() as cursor:
            add_query = f"SELECT * FROM invoice_table WHERE id={id_};"
            cursor.execute(add_query)
            connection.commit()
            print("invoice got...")
            result = cursor.fetchone()
            return result
