Проект для выгрузки данных с сайта статистики решения задач на платформе IT-resume по API, загрузки данных в локальную базу PostgreSQL, логирования процесса загрузки/выгрузки и отражения результатов анализа на дашборде Metabase.

Интеграция с обучающей платформой (LIS система) реализована с применением стандарта LTI (Learning Tools Interoperability). LIS (Learning Information System) система - система управления данными студентов.

Логи выгрузки:
- начало загрузки
- ошибка доступа
- преобразование строки
- завершение загрузки

Также в проекте реализована выгрузка ежедневной статистики решения задач в гугл-таблицу по API и отправка письма с ежедневной статистикой на почту (ввиду ограничения облачного сервера, отправка письма реализована только с локального терминала).

Метрики статитики LIS представлены в Metabase по ссылке http://89.104.71.90:3001/public/dashboard/23c18a65-bebb-4280-976b-26c0a7c5e505
