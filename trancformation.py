from datetime import datetime
import logging
import json
import ast


class Transformation:
    """
    Класс для преобразования списка статистик.
    """
    def __init__(self) -> None:
        self.passback_params = {
            'oauth_consumer_key': '',
            'lis_result_sourcedid': '',
            'lis_outcome_service_url': ''
        }

    @staticmethod
    def __prepare_passback_params(passback_params_str: str):
        """Преобразует строку passback_params в словарь."""
        if isinstance(passback_params_str, dict):
            return passback_params_str
        logging.info(f'Преобразуем строку {passback_params_str} в словарь.')
        try:
            # Сначала пробуем как JSON (если кавычки двойные)
            logging.info('Строка преобразована.')
            return json.loads(passback_params_str)
        except json.JSONDecodeError:
            try:
                # Пробуем как Python-словарь (если кавычки одинарные)
                logging.info('Строка преобразована.')
                return ast.literal_eval(passback_params_str)
            except (SyntaxError, ValueError) as err:
                # Возвращаем пустой словарь в случае ошибки
                logging.error(
                    f'{err}. Строка не преобразована. Словарь пустой.',
                    exc_info=True
                    )
                return {
                    'oauth_consumer_key': '',
                    'lis_result_sourcedid': '',
                    'lis_outcome_service_url': ''}

    @staticmethod
    def __validated_data(attemps: dict, passback_params: dict):
        """
        Проверяет данные.

        Args:
        attemps (dict): словарь пользовательской статистики.
        passback_params (dict): словарь параметров обратной передачи.
        """
        # Заполнение незаполненных passback_params
        passback_params['lis_result_sourcedid'] = passback_params.get(
            'lis_result_sourcedid', None
            )
        passback_params['lis_outcome_service_url'] = passback_params.get(
            'lis_outcome_service_url', None
            )

        # Проверка строковых типов:
        # строковых и заполненных
        if any(
            (
                not isinstance(attemps['lti_user_id'], str),
                not isinstance(attemps['attempt_type'], str),
                not isinstance(attemps['created_at'], str),
                not isinstance(passback_params['oauth_consumer_key'], str)
                )
        ):
            raise Exception('Неверный тип данных.')
        # строковых или пустых
        elif (not isinstance(
                    passback_params['lis_outcome_service_url'], (str, type(None))
                    )) or (
                        not isinstance(
                            attemps['is_correct'], (int, type(None))
                )) or (
                not isinstance(
                    passback_params['lis_result_sourcedid'], (str, type(None))
                )
        ):
            raise Exception('Неверный тип данных решения задач (is_correct).')

        # Проверка даты
        try:
            datetime.strptime(attemps['created_at'], '%Y-%m-%d %H:%M:%S.%f')
        except ValueError:
            raise ValueError('Неверный формат даты.')

        return True

    def get_statistics(self, statistics: list) -> dict:
        """
        Возвращает словарь статистики.

        Args:
        statistics (list): список статистик решения задач.

        Returns:
        dict: преобразованный список статистик:
        user_id - id пользователя,
        oauth_consumer_key - аутинфитикатор пользователя,
        lis_result_sourcedid - идентификатор, связывающий попытку пользователя с задачей,
        lis_outcome_service_url - URL для отправки оценки,
        is_correct - флаг успешного решения задачи,
        attempt_type - тип решения (отладка или отправка на проверку),
        created_at - время решения задачи.
    """
        if not statistics:
            raise Exception('Нет статистики.')

        result = []
        for statistic in statistics:
            passbaks_params = self.__prepare_passback_params(
                statistic['passback_params']
                )
            if not self.__validated_data(statistic, passbaks_params):
                continue  # Пропускаем невалидные записи

            result.append({
                'user_id': statistic['lti_user_id'],
                'oauth_consumer_key': passbaks_params['oauth_consumer_key'],
                'lis_result_sourcedid': passbaks_params['lis_result_sourcedid'],
                'lis_outcome_service_url': passbaks_params['lis_outcome_service_url'],
                'is_correct': statistic['is_correct'],
                'attempt_type': statistic['attempt_type'],
                'created_at': datetime.strptime(
                    statistic['created_at'], '%Y-%m-%d %H:%M:%S.%f'
                )
            })
            logging.info(f'Добавлена запись user_id {statistic["lti_user_id"]}')

        return result