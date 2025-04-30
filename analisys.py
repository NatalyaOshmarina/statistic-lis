from datetime import datetime
import logging
from collections import Counter
import configparser
import gspread
from oauth2client.service_account import ServiceAccountCredentials

config = configparser.ConfigParser()
config.read('config.ini')


class Analysis:
    """
    Класс вычисления статистики решения задач за день
    и выгрузки статистики в гугл-таблицу.
    """
    def __init__(self, data) -> None:
        self.data = data

    def __calculation_cnt_attempts(self):
        """
        Вычисляет статистику за отчетный день.

        Args:
        data (list): список статистик решения задач.

        Returns:
        dict: итоговый список статистик:
        date - отчетная дата,
        cnt_attemps - количество попыток,
        min_time - время первого входа на платформу,
        max_time - время последнего входа на платформу,
        most_popular_hour - час самых активных пользовательских сессий,
        cnt_correct - количество успешных решений,
        cnt_users - количество студентов, решавших задачи.
        """
        if not self.data:
            return {}

        hours = list()
        for user in self.data:
            user['hour'] = user.get('hour', user['created_at'].hour)
            hours.append(user['hour'])

        counter = Counter(list(hours))

        most_popular_hour = counter.most_common(1)[0]
        current_date = (self.data[0]['created_at']).date()
        min_time = datetime.strftime(
            min(
                self.data,
                key=lambda x: x['created_at']
                )['created_at'],
                '%Y-%m-%d %H:%M:%S'
            )
        max_time = datetime.strftime(
            max(
                self.data,
                key=lambda x: x['created_at']
                )['created_at'],
                '%Y-%m-%d %H:%M:%S'
            )
        correct_solution = list(filter(lambda x: x['is_correct'] == 1, self.data))
        cnt_users = set([user['user_id'] for user in res])
        result = {
            'date': current_date,
            'cnt_attemps': len(self.data),
            'min_time': min_time,
            'max_time': max_time,
            'most_popular_hour': most_popular_hour,
            'cnt_correct': len(correct_solution),
            'cnt_users': len(set(cnt_users))
            }

        return result

    def load_table(self):
        dt = self.__calculation_cnt_attempts()
        # Преобразуем словарь в список списков
        data_for_sheets = [[k, str(v)] for k, v in dt.items()]  # str(v) на случай datetime
        scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            config['Access']['JSON_API_GOOGLE'], scope
        )
        client = gspread.authorize(creds)
        sheet = client.open_by_key(config['Access']['ID_KEY_API_GOOGLE']).sheet1
        try:
            sheet.update(values=data_for_sheets, range_name="A1")
            logging.info('Данные успешно загружены в Google Sheets')
        except Exception as err:
            logging.error(f'Ошибка при загрузке в Google Sheets: {err}')
