import os
import telebot
from telebot import types
import json
import time
import sys
from datetime import datetime, timedelta
import logging
import pytz

# Загрузка конфигурации
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
                    filemode='w')

# Создание бота
bot = telebot.TeleBot(config['token'])

def printt(info):
    now = datetime.now(tz=moscow_tz)
    current_time = now.strftime(f"%Y-%m-%d %H:%M:%S")
    print(f"[{current_time}] - {info}")

def on_ready():
    printt(f"BOT ACTIVATED!")
    logger.info('BOT ACTIVATED!')

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

# Функция для создания клавиатуры с кнопкой "Назад"
def create_back_button():
    keyboard = types.InlineKeyboardMarkup()
    button_back = types.InlineKeyboardButton("Назад", callback_data='back')
    keyboard.row(button_back)
    return keyboard

# Обработка команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    try:
        keyboard = types.InlineKeyboardMarkup()
        button_about = types.InlineKeyboardButton("О нас", callback_data='about')
        button_FAQ = types.InlineKeyboardButton("FAQ", callback_data='FAQ')
        keyboard.row(button_about, button_FAQ)
        photo_path = 'img/LogoNeiroFood.jpg'
        bot.send_photo(message.chat.id, photo=open(photo_path, 'rb'), caption='Привет! Я ваш личный ассистент NeiroFood!\n', reply_markup=keyboard)
        log(message)
    except Exception as e:
        printt(f"Ошибка при отправке изображения: {e}")
        logger.info(f'{e}')

@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.reply_to(message, f"Список доступных команд:\n\n{command_name(0)} - приветствие\n{command_name(1)} - справка")
    log(message)

# Обработка нажатий на кнопки
@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    if call.data == 'about':
        text = '''
*Проект NeiroFood 🍔*

Привет! Мы - студенты, создали проект *NeiroFood* в рамках курса Интернет-Маркетинга. Это бургерная, где мы используем нейросети для создания уникальных рецептов бургеров. Приходите попробовать! 🍔✨'''
        photo_path = 'img/AboutNeiroFood.jpg'
        media = types.InputMediaPhoto(open(photo_path, "rb"), caption=text, parse_mode="Markdown")
        bot.edit_message_media(media , call.message.chat.id, call.message.id, reply_markup=create_back_button())
    elif call.data == 'FAQ':
        text = '''*1. Что такое "NeiroFood"?*
*NeiroFood* - это бургерная 🍔, созданная студентами в рамках курса Интернет-Маркетинга. Мы используем нейросети для создания уникальных рецептов бургеров.

*2. Как я могу сделать заказ?*
Для оформления заказа выберите бургер из меню и следуйте инструкциям нашего бота. Мы доставим ваш заказ в указанное место в кратчайшие сроки.

*3. Есть ли у вас программы лояльности или скидки для постоянных клиентов?*
В настоящее время мы еще не предлагаем программы лояльности или акции для постоянных клиентов, но активно работаем над этим. Следите за нашими обновлениями в нашем телеграм-канале или в приложении.

*4. Как я могу связаться с вашей поддержкой в случае возникновения проблем?*
Для связи с нашей поддержкой вы можете написать нам через телеграм-бота или позвонить по указанному номеру телефона, так же у нас имеется сайт.'''
        photo_path = 'img/FAQNeiroFood.jpg'
        media = types.InputMediaPhoto(open(photo_path, "rb"), caption=text, parse_mode="Markdown")
        bot.edit_message_media(media , call.message.chat.id, call.message.id, reply_markup=create_back_button())
    elif call.data == 'back':
        handle_start(call.message)



if __name__ == '__main__':
    try:
        on_ready()
        bot.polling()
    except Exception as e:
        printt(f"Ошибка при работе бота: {e}")
        logger.info(f"Ошибка при работе бота: {e}")
