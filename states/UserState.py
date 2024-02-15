from telebot.handler_backends import State, StatesGroup


class UserStates(StatesGroup):
    Convert_currency = State()
    CurrencyTo = State()
    Amount = State()
