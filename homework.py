import os
import time
import requests
import telegram
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv


logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s, %(levelname)s, %(name)s, %(message)s",
                    filename="api_sp1_bot/main.log",
                    filemode="a")

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler_steam = logging.StreamHandler()
handler_steam.setLevel(logging.DEBUG)
handler_rotate = RotatingFileHandler("api_sp1_bot/main.log",
                                     maxBytes=50000,
                                     backupCount=3)
logger.addHandler(handler_steam)
logger.addHandler(handler_rotate)


load_dotenv()


PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# инициализация бота
bot = telegram.Bot(token=TELEGRAM_TOKEN)


def parse_homework_status(homework):
    homework_name = homework["homework_name"]
    if homework["status"] == "rejected":
        verdict = "К сожалению, в работе нашлись ошибки."
    elif homework["status"] == "reviewing":
        verdict = "Работа принята на ревью."
    else:
        verdict = "Ревьюеру всё понравилось, работа зачтена!"
    return f"У вас проверили работу '{homework_name}'!\n\n{verdict}"


def get_homeworks(current_timestamp):
    '''Get all homeworks'''
    url = "https://praktikum.yandex.ru/api/user_api/homework_statuses/"
    headers = {"Authorization": f"OAuth {PRAKTIKUM_TOKEN}"}
    payload = {"from_date": current_timestamp}
    homework_statuses = requests.get(url, headers=headers, params=payload)
    return homework_statuses.json()


def send_message(message):
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = 0  # int(time.time())  # Начальное значение timestamp
    status_after = None
    while True:
        try:
            # получим последнюю домашку
            homework = get_homeworks(current_timestamp)["homeworks"][0]
            status_before = homework["status"]
            # если статус домашки изменился, то отправляем сообщение
            if status_before != status_after:
                message = parse_homework_status(homework)
                send_message(message)
                status_after = status_before
            time.sleep(5 * 60)  # Опрашивать раз в пять минут
        except Exception as e:
            logging.error(e, exc_info=True)
            message = f'Бот упал с ошибкой: {e}'
            send_message(message)
            time.sleep(5)


if __name__ == '__main__':
    main()
