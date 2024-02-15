from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from typing import Optional


def amount() -> Optional[ReplyKeyboardMarkup]:
    values = ['100', '200', '300', '400', '500']
    destinations = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    for digit in values:
        destinations.add(KeyboardButton(text=digit))
    return destinations
