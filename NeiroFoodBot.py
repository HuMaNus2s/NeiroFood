import os
import telebot
from telebot import types
import json
import time
import sys
from datetime import datetime, timedelta
import logging
import pytz

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

bot = telebot.TeleBot(config['token'])
#================================================================================= Неизменяемые функции
def printt(info):
    now = datetime.now(tz=moscow_tz)
    current_time = now.strftime(f"%Y-%m-%d %H:%M:%S")
    print(f"[{current_time}] - {info}")

def on_ready():
    printt(f"BOT ACTIVATED!")
    logger.info('BOT ACTIVATED!')
#================================================================================= Записи логов
def log(message=None, error=False, button=None):
    if not error and not button: # Лог использования команды
        printt(f'{message.from_user.username} использовал команду <{message.text}>')
        logger.info(f'{message.from_user.username} использовал команду <{message.text}>')
    elif not error and button: # Лог использования кнопки
        printt(f'{message.from_user.username} использовал кнопку <{button}>')
        logger.info(f'{message.from_user.username} использовал кнопку <{button}>')
    else: # Лог ошибки использования команды
        printt(f'Неизвестная команда <{message.text}>')
        logger.info(f'Неизвестная команда <{message.text}>')
#================================================================================= Команды
@bot.message_handler(commands=['start'])
def handle_start(message):
    try:
        keyboard = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton("О нас", callback_data='about')
        button2 = types.InlineKeyboardButton("FAQ", callback_data='FAQ')
        keyboard.row(button1, button2)
        photo_path = 'img/LogoNeiroFood.jpg'
        bot.send_photo(message.chat.id, photo=open(photo_path, 'rb'), caption='Привет! Я ваш личный ассистент NeiroFood!\n Меню:', reply_markup=keyboard)
        log(message)
    except Exception as e:
        printt(f"Ошибка при отправке изображения: {e}")
        logger.info(f'{e}')


@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.reply_to(message, f"Список доступных команд:\n\n{command_name(0)} - приветствие\n{command_name(1)} - справка")
    log(message)
#================================================================================= Обработка кнопок
@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    message = call.message
    if call.data == 'about': # О нас
        text = '''
Проект NeiroFood

Привет! Мы - студенты, создали проект "NeiroFood" в рамках курса Интернет-Маркетинга. Это бургерная, где мы используем нейросети для создания уникальных рецептов бургеров. Приходите попробовать! 🍔✨'''
        bot.send_message(message.chat.id, text)
        log(message, False, call.data)
    elif call.data == 'FAQ': # FAQ
        text = '''1. Что такое "NeiroFood"?
"NeiroFood" - это бургерная, созданная студентами в рамках курса Интернет-Маркетинга. Мы используем нейросети для создания уникальных рецептов бургеров.
2. Как я могу ознакомиться с вашим меню?
Меню доступно в нашем телеграм-боте. Просто нажмите кнопку "Меню" для просмотра.
3. Как я могу сделать заказ?
Для оформления заказа выберите бургер из меню и следуйте инструкциям нашего бота. Мы доставим ваш заказ в указанное место в кратчайшие сроки.
4. Какие способы оплаты вы принимаете?
Мы принимаем оплату наличными и через онлайн-платформы, такие как карты и электронные кошельки.
5. Есть ли у вас программы лояльности или скидки для постоянных клиентов?
В настоящее время мы еще не предлагаем программы лояльности или акции для постоянных клиентов, но активно работаем над этим. Следите за нашими обновлениями в нашем телеграм-канале или в приложении.
6. Как я могу связаться с вашей поддержкой в случае возникновения проблем?
Для связи с нашей поддержкой вы можете написать нам через телеграм-бота или позвонить по указанному номеру телефона.
7. Какие часы работы у вас?
Мы работаем ежедневно с 9:00 до 15:50.'''
        bot.send_message(message.chat.id, text)
        log(message, False, call.data)

#================================================================================= Текстовые команды
@bot.message_handler(func=lambda message: True)
def handle_text_messages(message):
    if message.text == 'Привет':
        bot.reply_to(message, f"Приветствую! Рад тебя видеть!")
    else:
        send_unknown_command_message(message)

def send_unknown_command_message(message):
    bot.reply_to(message, f"Извините, я не понимаю эту команду. Попробуйте {command_name(1)}.")
    log(message, True)
#=================================================================================
if __name__ == '__main__':
    try:
        on_ready()
        bot.polling()
    except Exception as e:
        printt(f"Ошибка при работе бота: {e}")
        logger.info(f"Ошибка при работе бота: {e}")
