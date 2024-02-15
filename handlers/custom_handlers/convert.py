from telebot.types import Message, ReplyKeyboardRemove
from keyboards.reply.amount import amount
from keyboards.reply.currencies_list_reply import currencies_reply
from loader import bot
from states.UserState import UserStates
from utils.misc.logging import logging_func
from utils.misc.requests_to_api import get_request


@bot.message_handler(commands=["convert"])
@logging_func
def convert_value(message: Message):
    bot.send_message(message.chat.id, f'Какую валюту конвертируем?', reply_markup=currencies_reply())
    bot.set_state(user_id=message.from_user.id, state=UserStates.CurrencyTo, chat_id=message.chat.id)


@bot.message_handler(state=UserStates.CurrencyTo)
@logging_func
def currency_to(message: Message):
    if message.text in ('RUB', 'USD', 'EUR'):
        with bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data:
            data['currency_to'] = message.text
        bot.set_state(user_id=message.from_user.id, state=UserStates.Amount, chat_id=message.chat.id)
        bot.send_message(message.chat.id, f'На какую валюту хотите обменять {data["currency_to"]}?',
                         reply_markup=currencies_reply())
    else:
        bot.send_message(message.chat.id, f'Введите корректную валюту, например: RUB')


@bot.message_handler(state=UserStates.Amount)
@logging_func
def convert_value(message: Message):
    if message.text in ('RUB', 'USD', 'EUR'):
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['currency_into'] = message.text
        bot.send_message(message.chat.id, f'Введите сумму, которую хотите конвертировать:',
                         reply_markup=amount())
        bot.set_state(user_id=message.from_user.id, state=UserStates.Convert_currency, chat_id=message.chat.id)
    else:
        bot.send_message(message.chat.id, f'Введите корректную валюту, например: USD')


@bot.message_handler(state=UserStates.Convert_currency)
@logging_func
def convert_value(message: Message):
    if message.text.isdigit():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['amount'] = message.text
        bot.send_message(message.chat.id, f'Конвертируем {data["currency_to"]} в {data["currency_into"]}...')
        querystring = {"from": data["currency_to"], "to": data["currency_into"], "amount": [data["amount"]]}
        response = get_request(param=querystring)
        converted_currency = response.get('result', 'No result')
        bot.send_message(chat_id=message.chat.id,
                         text=f'При пересчете с {data["currency_to"]} вышло '
                              f'{converted_currency} {data["currency_into"]}', reply_markup=ReplyKeyboardRemove())
        bot.delete_state(user_id=message.from_user.id, chat_id=message.chat.id)
    else:
        bot.send_message(message.chat.id, f'Введите цифры, без букв')
