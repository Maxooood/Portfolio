from telebot.types import Message
from loader import bot
from utils.misc.logging import logging_func


# Эхо хендлер, куда летят текстовые сообщения без указанного состояния
@bot.message_handler(state=None)
@logging_func
def bot_echo(message: Message):
    hello = ('привет', 'здарова', 'здравствуйте', 'добрый день', 'добрый вечер', 'доброе утро', 'приветствую вас',
             'желаю здравствовать', 'моё почтение', 'душевно рад вас видеть', 'безмерно рад встречи',
             'сердечный поклон вам', 'сердечно рад вам', 'сколько лет', 'сколько зим', 'разрешите вас приветствовать',
             'салют', 'Пламенный привет', 'хай', 'хелло', 'приветствую вас', 'доброй ночи', 'приветик',
             'мир вашему дому', 'доброго здоровья', 'рад вас видеть', 'всем добра', 'рад встрече с вами', 'приветствую'
             )
    goodbye = ('пока', 'до свидания', 'ещё увидимся', 'до скорой встречи', 'прощайте', 'всего хорошего', 'счастливо',
               'до завтра', 'доброго пути', 'будьте здоровы', 'всегда рады вас видеть', 'приятно было познакомиться',
               'всего доброго', 'счастливого пути', 'счастливо оставаться', 'до вечера',
               'надеюсь ещё раз увидеться с вами', 'до новой встречи', 'всегда рады вас видеть', 'будьте здоровы',
               'разрешите откланяться', 'чао', 'доброй ночи')
    if message.text.lower() in hello:
        bot.send_message(message.chat.id, f'Здравствуйте')
    elif message.text.lower() in goodbye:
        bot.send_message(message.chat.id, f'До свидания')
    else:
        bot.send_message(message.from_user.id, f"Команды не найдено. Выберите одну из списка:\n"
                                               f"/start\n"
                                               f"/help\n"
                                               f"/convert")

