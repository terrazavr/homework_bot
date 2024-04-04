import os
import logging

import requests
import time

from http import HTTPStatus

import telegram

from dotenv import load_dotenv

from exceptions import (
    StatusError,
    APIErrorException,
    OKStatusError,
    TelegramError
)

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 300
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    level=logging.CRITICAL,
    filename='my_logs.log',
    encoding='UTF-8',
    format='%(asctime)s, %(levelname)s, %(message)s'
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(name)s')

stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)
stream_handler.setFormatter(formatter)


def check_tokens():
    """Проверяет доступность переменных.
    Они нужны для работы бота,
    если отсутствует хоть одна - бот не должен работать.
    """
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат.
    Принимает на вход 2 параметра:
    экземпляр класса Bot и стороку с текстом сообщения.
    """
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug(f'В {TELEGRAM_CHAT_ID} отправленно - {message}')
    except telegram.error.TelegramError as error:
        logger.error(f'Ошибка отправки сообщения - {error}')
        raise TelegramError(f'Ошибка отправки  в телеграм сообщения: {error}')


def get_api_answer(current_timestamp):
    """
    Делает запрос к единственному эндпоинту API-сервиса.
    В качестве параметра передается временная метка.
    """
    timestamp = current_timestamp or int(time.time())
    playload = {'from_date': timestamp}
    try:
        homework_statuses = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=playload
        )
    except requests.RequestException:
        logger.error(f'Сбой в работе программы: '
                     f'Эндпоинт {ENDPOINT} недоступен.')
        raise APIErrorException('Ошибка запроса к API: {error}.')
    if homework_statuses.status_code != HTTPStatus.OK:
        raise OKStatusError(f'Ошибка {homework_statuses.status_code}')
    return homework_statuses.json()


def check_response(response):
    """
    Проверяет ответ API на соответствие документации.
    В качестве параметра функция получает ответ API,
    приведенный к типам данных Python.
    """
    if not isinstance(response, dict):
        raise TypeError('Ответ API отличен от словаря')
    elif 'homeworks' not in response:
        raise KeyError('Ошибка словаря по ключу homeworks')
    elif not isinstance(response['homeworks'], list):
        raise TypeError('Неверный тип данных в API')
    return response.get('homeworks')


def parse_status(homework):
    """Получает информацию о конкретной домашке.
    В случае успеха возвращает строку с одним из вердиктов.
    """
    homework_name = homework.get('homework_name')
    status = homework.get('status')
    if status is None:
        raise StatusError('Отсутсвует статус работы')
    if status not in HOMEWORK_VERDICTS:
        raise StatusError('Неверный статус работы')
    if homework_name is None:
        raise StatusError('Нет ключа домашней работы')
    verdict = HOMEWORK_VERDICTS[status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logger.critical('Отсутствует обязательная переменная окружения. '
                        'Программа принудительно остановлена.')
        exit()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    message = 'Привет, я работаю!'
    send_message(bot, message)
    while True:
        try:
            response = get_api_answer(timestamp)
            hw_status = check_response(response)
            if not hw_status:
                send_message(bot, 'Изменений пока нет')
                logger.debug('Изменений пока нет')
            else:
                new_message = parse_status(hw_status[0])
                send_message(bot, f'Статус домашней работы '
                             f'обновлен - {new_message}')
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.exception(message)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
