from datetime import datetime, timedelta
import logging
import os
import ssl
import smtplib
from email.message import EmailMessage
import configparser
from extraction import Extraction
from trancformation import Transformation
from analisys import Analysis
from loading import Database

config = configparser.ConfigParser()
config.read('config.ini')


# Формируем имя файла с логами
current_date = datetime.now().strftime('%Y%m%d.log')
folder = config['Files']['FILE_PATH']

# Создаем папку для логов (если не существует)
os.makedirs(folder, exist_ok=True)

# Полный путь к файлу логов
log_file_path = os.path.join(folder, current_date)

# Явная настройка логгера
logger = logging.getLogger()
logger.handlers.clear()

# Создаем и настраиваем файловый обработчик
file_handler = logging.FileHandler(log_file_path, mode='a')
file_handler.setLevel(logging.INFO)  # Уровень для файла
file_handler.setFormatter(
    logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S')
)

# Проверка доступности файла
try:
    with open(log_file_path, 'a'):
        pass
    print('Файл доступен для записи логов.')
except IOError as err:
    print(f"Ошибка доступа к файлу: {err}")

# Добавляем обработчик к логгеру
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)

# Удаление файлов через через три дня
day_for_drop = datetime.strptime(current_date, '%Y%m%d.log') - timedelta(days=2)
content = os.listdir(folder)
for file in content:
    file_path = os.path.join(folder, file)  # Полный путь к файлу
    try:
        file_date = datetime.strptime(file, '%Y%m%d.log')
        if file_date < day_for_drop:
            os.remove(file_path)
            print(f'Файл {file} удален из папки.')
    except ValueError as err:
        print(f'Файл {file} имеет неверный формат имени: {err}')
    except FileNotFoundError as err:
        print(f'{err}. Файл {file_path} не найден.')
    except PermissionError:
        print('Нет прав на удаление')
    except Exception as err:
        print(f'Произошла ошибка: {err}')


extractor = Extraction()
dt = extractor.get_data()
transformation = Transformation()
dt_normal = transformation.get_statistics(dt)
data = Database()
data.post(dt_normal)
analis = Analysis(dt_normal)
analis.load_table()

# Настройки SMTP-сервера
SMTP_SERVER = 'smtp.mail.ru'
SMTP_PORT = 465
EMAIL = config['Access']['EMAIL_FROM']
PASSWORD = config['Access']['KEY_EMAIL']

context = ssl.create_default_context()

# Создаём письмо
msg = EmailMessage()
msg['Subject'] = 'Отчет по статистике решения задач'
msg['From'] = EMAIL
msg['To'] = config['Access']['EMAIL_TO']
msg.set_content(f'Добрый день.\n Статистика решения задач за {datetime.now().date()} {config["Access"]["URL_SHEET"]}')

try:
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=ssl.create_default_context()) as server:
        server.login(EMAIL, PASSWORD)
        server.send_message(msg)
        print('Письмо успешно отправлено через SMTP_SSL!')
except Exception as err:
    print(f'Ошибка при отправке письма: {err}')
