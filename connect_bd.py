import psycopg2

host = "45.80.69.152"
user = "postgres"
password = "220508qQ"
db_name = "ShopDB"
port = 5432


def connect_data_b():
    try:
        connection = psycopg2.connect(
            host=host, user=user, password=password, database=db_name
        )
        connection.autocommit = True
        cursor = connection.cursor()
        return connection, cursor
    except psycopg2.Error as e:
        print(f"Ошибка подключения к базе данных: {e}")
        raise
