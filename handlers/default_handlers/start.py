from telebot.types import Message, ReplyKeyboardRemove
from loader import bot
from utils.misc.logging import logging_func


@bot.message_handler(commands=["start"])
@logging_func
def bot_start(message: Message):
    bot.send_message(message.from_user.id, f"Доброго времени суток, {message.from_user.full_name}!",
                     reply_markup=ReplyKeyboardRemove())
    bot.send_message(message.chat.id, f"Бот предназначен для конвертации валюты в режиме реального времени\n"
                                      f"Можете ознакомиться с командами бота нажав - /help")





