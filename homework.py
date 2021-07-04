import logging
import os
import time
from logging.handlers import RotatingFileHandler
from typing import Dict, List, Optional

import requests
from requests.exceptions import RequestException
from requests.models import HTTPError
import telegram
from dotenv import load_dotenv


logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s, %(levelname)s, %(name)s, %(message)s",
                    filename="main.log",
                    filemode="a")

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler_rotate = RotatingFileHandler("main.log",
                                     maxBytes=50000,
                                     backupCount=3)
handler_steam = logging.StreamHandler()

logger.addHandler(handler_rotate)
logger.addHandler(handler_steam)


load_dotenv()


URL: str = "https://praktikum.yandex.ru/"
PRAKTIKUM_TOKEN: str = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN: str = os.getenv('TELEGRAM_TOKEN')
CHAT_ID: int = os.getenv('TELEGRAM_CHAT_ID')

# инициализация бота
bot = telegram.Bot(token=TELEGRAM_TOKEN)


def parse_homework_status(homework):
    homework_keys: List[str] = ["homework_name", "status"]
    homework_status: List[str] = ["rejected", "reviewing", "approved"]
    # проверяем наличие ключей
    exists_keys: bool = all(element in homework for element in homework_keys)
    if exists_keys:
        exists_status: bool = homework["status"] in homework_status
        if not exists_status:
            return "Неверный ответ сервера"
    else:
        return "Неверный ответ сервера"
    homework_name: str = homework["homework_name"]
    if homework["status"] == "rejected":
        verdict = "К сожалению, в работе нашлись ошибки."
    elif homework["status"] == "reviewing":
        verdict = "Работа принята на ревью."
    else:
        verdict = "Ревьюеру всё понравилось, работа зачтена!"
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    '''Get all homeworks'''
    url_add: str = "api/user_api/homework_statuses/"
    url: str = URL + url_add
    headers: str = {"Authorization": f"OAuth {PRAKTIKUM_TOKEN}"}
    payload: Dict[str, int] = {"from_date": current_timestamp}
    try:
        homework_statuses = requests.get(url,
                                         headers=headers,
                                         params=payload,
                                         timeout=60)
        if 400 <= homework_statuses.status_code < 500:
            raise HTTPError("Client error, request status = "
                            f"{homework_statuses.status_code}")
        elif 500 <= homework_statuses.status_code < 600:
            raise HTTPError("Server error, request status = "
                            f"{homework_statuses.status_code}")
    except RequestException as e:
        logging.error(e, exc_info=True)
        return {}
    return homework_statuses.json()


def send_message(message):
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp: int = int(time.time())  # Начальное значение timestamp
    status_after: Optional[str] = None
    homeworks_key = ["homeworks"]
    while True:
        try:
            # проверим что есть ключ homeworks
            homeworks_check = get_homeworks(current_timestamp)
            is_homeworks_key = any(element in homeworks_key
                                   for element in homeworks_check)
            if is_homeworks_key:
                # получим домашки
                homeworks: List = homeworks_check["homeworks"]
            else:
                continue
            # проверяем наличие домашек
            if len(homeworks) > 0:
                # получим последнюю домашку
                homework: Dict = homeworks[0]
                status_before: str = homework["status"]
                # если статус домашки изменился, то отправляем сообщение
                if status_before != status_after:
                    message: str = parse_homework_status(homework)
                    send_message(message)
                    status_after = status_before
                time.sleep(5 * 60)  # Опрашивать раз в пять минут
            else:
                continue
        except Exception as e:
            logging.error(e, exc_info=True)
            message: str = f'Бот упал с ошибкой: {e}'
            send_message(message)
            time.sleep(5)


if __name__ == '__main__':
    main()
