import os
from dotenv import load_dotenv, find_dotenv
from utils.misc.logging import logger


if not find_dotenv():
    logger.log_error("Переменные окружения не загружены т.к отсутствует файл .env")
else:
    load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
RAPID_API_KEY = os.getenv("RAPID_API_KEY")
head = {"X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "currency-conversion-and-exchange-rates.p.rapidapi.com"}
DEFAULT_COMMANDS = (
    ("start", "Функционал бота"),
    ("convert", "Расчет валюты"),
    ("help", "Команды")
)
