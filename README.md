# api_sp1_bot
## Описание
Бот для телеграмм. Собирает данные о статусе домашнего задания по api яндекс.практикума и присылает сообщение в телеграмм.

## Технологии
- **Python 3.7.9**
- **Библиотека python-telegram-bot**

## Процедура запуска проекта

1. Клонировать репозиторий и перейти в него в командной строке:

git clone https://github.com/EvgeniyGartsev/api_sp1_bot
cd api_yamdb

2. Cоздать и активировать виртуальное окружение:
python3 -m venv venv
source venv/Scripts/activate

3. Обновить pip и установить зависимости из файла requirements.txt:
python -m pip install --upgrade pip
pip install -r requirements.txt

4. При запуске локально создать файл .env и прописать параметры окружения:
- PRAKTIKUM_TOKEN
- TELEGRAM_TOKEN
- TELEGRAM_CHAT_ID

5. При запуске на серевере прописать в параметры окружения:
- PRAKTIKUM_TOKEN
- TELEGRAM_TOKEN
- TELEGRAM_CHAT_ID

6. Запустить файл homework.py на исполнение.
python homework.py 