from datetime import datetime, timedelta
import requests
import logging
import configparser
import os

dirname = os.path.dirname(__file__)
config = configparser.ConfigParser()
config.read(os.path.join(dirname, 'config.ini'))


class Extraction:
    """
    Класс для импорта статистики решения задач с API
    """
    URL_STATISTICS = 'https://b2b.itresume.ru/api/statistics'
    BASE_PARAMS = {
      'client': config['Access']['CLIENT'],
      'client_key': config['Access']['CLIENT_KEY']
    }

    def __init__(self) -> None:
        self.start = datetime.now() - timedelta(days=365*2)
        self.interval = timedelta(hours=24)
        self._params_gen = self.__get_params()

    @property
    def get_start(self):
        return self.start

    @property
    def get_interval(self):
        return self.interval

    def __get_params(self):
        while True:
            # Создаём новый словарь на основе BASE_PARAMS
            params = self.BASE_PARAMS.copy()
            end = self.start + self.interval
            params['start'] = self.start
            params['end'] = end
            yield params
            # Обновляем start для следующей итерации
            self.start = end

    def get_data(self):
        logging.info(f'Выгружаем данные с {Extraction.URL_STATISTICS}.')
        params = next(self._params_gen)
        try:
            r = requests.get(
                Extraction.URL_STATISTICS,
                params=params
            )
            r.raise_for_status()
            logging.info(f'Данные выгружены.')
            return r.json()
        except requests.exceptions.HTTPError as err:
            logging.error(f'HTTPError: {err }', exc_info=True)
            return(f'HTTP Error: {err}')
        except requests.exceptions.RequestException as err:
            logging.error(f'Request Error: {err}', exc_info=True)
            return(f'Request Error: {err}')