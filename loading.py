import configparser
import psycopg2
import logging
import os

dirname = os.path.dirname(__file__)
config = configparser.ConfigParser()
config.read(os.path.join(dirname, 'config.ini'))


class Database:
    """
    Класс для экспорта данных о продажах в PostgreSQL (Singlton)
    """
    HOST = config['Access']['HOST_SQL']
    PORT = 5432
    DATABASE = config['Access']['BASE_SQL']
    USER = config['Access']['USER_SQL']
    PASSWORD = config['Access']['PASSWORD_SQL']

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, autocommit=False):
        try:
            self.connection = psycopg2.connect(
                host=Database.HOST,
                port=Database.PORT,
                database=Database.DATABASE,
                user=Database.USER,
                password=Database.PASSWORD,
                client_encoding='UTF8'
            )

            if autocommit:
                self.connection.autocommit = True

            self.cursor = self.connection.cursor()
            self.primary_key = 0
            self._primary_key_gen = self.__get_primary_key()
        except Exception as err:
            logging.error(f'Ошибка инициализации БД: {err}')
            raise

    def __get_primary_key(self):
        while True:
            # Присваиваем значение первичного ключа
            yield self.primary_key
            # Обновляем значение первичного ключа для следующей итерации
            self.primary_key += 1

    @staticmethod
    def ensure_utf8(value):
        if isinstance(value, str):
            return value.encode('utf-8', 'ignore').decode('utf-8')
        elif isinstance(value, bytes):
            return value.decode('utf-8', 'ignore')
        return value

    def select(self, query, vars):
        self.cursor.execute(query, vars)
        res = self.cursor.fetchall()
        return res

    def post(self, data: list):
        if not data:
            logging.warning('Нет данных для загрузки.')
            return

        logging.info(f'Начало заполнения базы {Database.DATABASE}')

        try:
            for user in data:
                # Подготовка данных
                id = next(self._primary_key_gen)
                user['id'] = user.get('id', id)
                columns = ', '.join(user.keys())
                placeholders = ', '.join(['%s'] * len(user))
                values = [self.ensure_utf8(v) for v in user.values()]

                # Формирование и выполнение запроса
                query = f'INSERT INTO solvings ({columns}) VALUES ({placeholders})'
                self.cursor.execute(query, values)

                if not self.connection.autocommit:
                    self.connection.commit()

            logging.info('Заполнение базы завершено.')
        except Exception as err:
            logging.error(f'Ошибка при загрузке данных: {err}')
            self.connection.rollback()
            raise