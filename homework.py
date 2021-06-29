import logging
import os
import time
from logging.handlers import RotatingFileHandler

import requests
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


URL = "https://praktikum.yandex.ru/"
PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# инициализация бота
bot = telegram.Bot(token=TELEGRAM_TOKEN)


def parse_homework_status(homework):
    homework_keys = ["homework_name", "status"]
    homework_status = ["rejected", "reviewing", "approved"]
    # проверяем наличие ключей
    exists_keys = all(element in homework for element in homework_keys)
    if exists_keys:
        exists_status = homework["status"] in homework_status
        if not exists_status:
            return "Неверный ответ сервера"
    else:
        return "Неверный ответ сервера"
    homework_name = homework["homework_name"]
    if homework["status"] == "rejected":
        verdict = "К сожалению, в работе нашлись ошибки."
    elif homework["status"] == "reviewing":
        verdict = "Работа принята на ревью."
    else:
        verdict = "Ревьюеру всё понравилось, работа зачтена!"
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    '''Get all homeworks'''
    try:
        url_add = "api/user_api/homework_statuses/"
        url = URL + url_add
        headers = {"Authorization": f"OAuth {PRAKTIKUM_TOKEN}"}
        payload = {"from_date": current_timestamp}
        homework_statuses = requests.get(url,
                                         headers=headers,
                                         params=payload,
                                         timeout=5)
        homework_statuses.raise_for_status()
    except Exception as e:
        logging.error(e, exc_info=True)
    return homework_statuses.json()


def send_message(message):
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())  # Начальное значение timestamp
    status_after = None
    while True:
        try:
            # получим домашки
            homeworks = get_homeworks(current_timestamp)["homeworks"]
            # проверяем наличие домашек
            if len(homeworks) > 0:
                # получим последнюю домашку
                homework = homeworks[0]
                status_before = homework["status"]
                # если статус домашки изменился, то отправляем сообщение
                if status_before != status_after:
                    message = parse_homework_status(homework)
                    send_message(message)
                    status_after = status_before
                time.sleep(5 * 60)  # Опрашивать раз в пять минут
            else:
                continue
        except Exception as e:
            logging.error(e, exc_info=True)
            message = f'Бот упал с ошибкой: {e}'
            send_message(message)
            time.sleep(5)


if __name__ == '__main__':
    main()
