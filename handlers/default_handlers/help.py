from telebot.types import Message
from config_data.config import DEFAULT_COMMANDS
from loader import bot
from utils.misc.logging import logging_func, logger


@bot.message_handler(commands=["help"])
@logging_func
def bot_help(message: Message):
    text = [f"/{command} - {desk}" for command, desk in DEFAULT_COMMANDS]
    logger.log_debug(f"Commands: {text}")
    bot.send_message(message.chat.id, "\n".join(text))
