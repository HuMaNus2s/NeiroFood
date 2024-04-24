import os
import telebot
import json
import time
import sys
from datetime import datetime, timedelta
import logging
import pytz
#============================================================= Тех.часть: логи, конфиги, время
file_for_config = open('config.json', 'r')
config = json.load(file_for_config)
prefix = config['prefix']
def command_name(number):
    return prefix + commands[number]

if not os.path.exists('logs'):
    os.makedirs('logs')

moscow_tz = pytz.timezone('Europe/Moscow')
now = datetime.now(tz=moscow_tz)
current_time = now.strftime(f"%Y-%m-%d %H:%M:%S")
log_time = now.strftime("%Y-%m-%d_%H.%M")

logger = logging.getLogger('telegram')
logger_err = logging.getLogger('err')
log_file = "logs/NeiroFoodBot_{}.log".format(log_time)
logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s][%(name)s][%(levelname)s] - %(message)s',
                    filename=log_file, # Имя файла для логов
                    filemode='w') # Режим записи/создание файла - добавление новых записей в конец файла
#=================================================================================
bot = telebot.TeleBot(config['token']) # Активация бота
#================================================================================= Неизменяемые функции
def printt(info):
    print(f"[{current_time}] - {info}")
def on_ready():
    printt(f"BOT ACTIVATED!")
    logger.info('BOT ACTIVATED!')
def log(message, error=False):
    if not error:
        printt(f'{message.from_user.username} использовал команду <{message.text}>')
        logger.info(f'{message.from_user.username} использовал команду <{message.text}>')
    else:
        printt(f'Неизвестная команда <{message.text}>')
        logger.info(f'Неизвестная команда <{message.text}>')

#=================================================================================
commands=['start', 'help', 'about'] #Не менять порядок команд! Если изменить, то текста перепутаются
@bot.message_handler(commands)
def handle_start_help(message):
    if message.text == command_name(0): # Старт бота
        try:
            photo_path = 'img/LogoNeiroFood.jpg'
            bot.send_photo(message.chat.id, photo=open(photo_path, 'rb'), caption='Привет! Я ваш личный ассистент NeiroFood!\n Меню:')  
            log(message)
        except Exception as e:
            printt(f"Ошибка при отправке изображения: {e}")
            logger.info(f'{e}')
    elif message.text == command_name(1): # Помощь
        bot.reply_to(message, f"Список доступных команд:\n\n{command_name(0)} - приветствие\n{command_name(1)} - справка")
        log(message)

@bot.message_handler(func=lambda message: True)
def handle_text_messages(message):
    if message.text == 'Привет':
        bot.reply_to(message, f"Приветствую! Рад тебя видеть!")
    else:
        send_unknown_command_message(message)

def send_unknown_command_message(message):
    bot.reply_to(message, f"Извините, я не понимаю эту команду. Попробуйте {command_name(1)}.")
    log(message, True)

if __name__ == '__main__':
    try:
        on_ready()
        bot.polling()
    except Exception as e:
        printt(f"Ошибка при работе бота: {e}")
        logger.info(f"Ошибка при работе бота: {e}")
