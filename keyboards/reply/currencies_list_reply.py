from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from typing import Optional


def currencies_reply() -> Optional[ReplyKeyboardMarkup]:
    currency = ('USD', 'RUB', 'EUR')
    destinations = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    for bottom in currency:
        destinations.add(KeyboardButton(text=bottom))
    return destinations
