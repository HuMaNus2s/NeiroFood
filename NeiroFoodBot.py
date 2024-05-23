import os
import telebot
from telebot import types
import json
import logging
from datetime import datetime
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
log_time = now.strftime("%Y-%m-%d_%H.%M")

logger = logging.getLogger('telegram')
logger_err = logging.getLogger('err')
log_file = f"logs/NeiroFoodBot_{log_time}.log"
logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s][%(name)s][%(levelname)s] - %(message)s',
                    filename=log_file, 
                    filemode='w')

# Создание бота
bot = telebot.TeleBot(config['token'])

def printt(info):
    now = datetime.now(tz=moscow_tz)
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{current_time}] - {info}")

def on_ready():
    printt("BOT ACTIVATED!")
    logger.info('BOT ACTIVATED!')

def log(message=None, error=False, button=None):
    if not error and not button:
        printt(f'{message.from_user.username} использовал команду <{message.text}>')
        logger.info(f'{message.from_user.username} использовал команду <{message.text}>')
    elif not error and button:
        printt(f'{message.from_user.username} использовал кнопку <{button}>')
        logger.info(f'{message.from_user.username} использовал кнопку <{button}>')
    else:
        printt(f'Неизвестная команда <{message.text}>')
        logger.info(f'Неизвестная команда <{message.text}>')

# Работа с корзинами пользователей
def get_user_basket(user_id):
    file_path = f'users/{user_id}.json'
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    else:
        return {}

def save_user_basket(user_id, basket):
    file_path = f'users/{user_id}.json'
    if not os.path.exists('users'):
        os.makedirs('users')
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(basket, file, ensure_ascii=False, indent=4)

burgers = ['Ангус ШЕФ',
           'Двойной ВОППЕР',
           'Родео Бургер',
           'Цезарь КИНГ',
           'ЦЭНСИ',
           'Баварский бургер',
           'Черная МАМБА',
           'Зеленный ФРЕШ',
           'Двойной Чизбургер']

def back_button(call):
    keyboard = types.InlineKeyboardMarkup()
    button_back = types.InlineKeyboardButton("Назад", callback_data=call)
    keyboard.row(button_back)
    return keyboard

def menu_tool_button():
    keyboard = types.InlineKeyboardMarkup()
    button_about = types.InlineKeyboardButton("О нас", callback_data='about')
    button_FAQ = types.InlineKeyboardButton("FAQ", callback_data='FAQ')
    button_menu = types.InlineKeyboardButton("Меню", callback_data='menu')
    button_basket = types.InlineKeyboardButton("Корзина", callback_data='basket')
    keyboard.row(button_about, button_FAQ)
    keyboard.row(button_menu, button_basket)
    return keyboard

def menu_button():
    keyboard = types.InlineKeyboardMarkup()
    button_neiro_burger = types.InlineKeyboardButton("Нейро-бургеры", callback_data='neiro_burger')
    button_drinks = types.InlineKeyboardButton("Напитки", callback_data='drinks')
    button_combo = types.InlineKeyboardButton("Нейро-комбо", callback_data='combo')
    button_basket = types.InlineKeyboardButton("Корзина", callback_data='basket')
    back_button = types.InlineKeyboardButton("Назад", callback_data='back')
    keyboard.row(button_neiro_burger)
    keyboard.row(button_drinks)
    keyboard.row(button_combo)
    keyboard.row(button_basket)
    keyboard.row(back_button)
    return keyboard

def button_for_basket(burger_name, quantity=1):
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    minus_button = types.InlineKeyboardButton("-", callback_data=f'basket_remove_{burger_name}')
    basket_button = types.InlineKeyboardButton(f"{quantity} шт", callback_data='noop')
    plus_button = types.InlineKeyboardButton("+", callback_data=f'basket_add_{burger_name}')
    back_button = types.InlineKeyboardButton("Назад", callback_data='neiro_burger')
    keyboard.add(minus_button, basket_button, plus_button)
    keyboard.row(back_button)
    return keyboard

def button_for_burger(burger_name):
    keyboard = types.InlineKeyboardMarkup()
    basket_button = types.InlineKeyboardButton("Корзина", callback_data='basket')
    back_button = types.InlineKeyboardButton("Назад", callback_data='neiro_burger')
    keyboard.row(basket_button)
    keyboard.row(back_button)
    return keyboard

def menu_neiro_burger():
    keyboard = types.InlineKeyboardMarkup()
    for burger in burgers:
        button = types.InlineKeyboardButton(burger, callback_data=burger)
        keyboard.row(button)
    back_button = types.InlineKeyboardButton("Назад", callback_data='menu')
    keyboard.row(back_button)
    return keyboard

def display_basket(user_id):
    user_basket = get_user_basket(user_id)
    if user_basket:
        basket_text = "Ваша корзина:\n\n"
        for burger, quantity in user_basket.items():
            basket_text += f"{burger}: {quantity} шт.\n"
        basket_text += "\nВы можете добавить или удалить бургеры."
    else:
        basket_text = "Ваша корзина пуста."
    return basket_text

def basket_button(user_id):
    keyboard = types.InlineKeyboardMarkup()
    user_basket = get_user_basket(user_id)
    if user_basket:
        for burger, quantity in user_basket.items():
            minus_button = types.InlineKeyboardButton(f"- {burger}", callback_data=f'basket_remove_{burger}')
            plus_button = types.InlineKeyboardButton(f"+ {burger}", callback_data=f'basket_add_{burger}')
            keyboard.row(minus_button, plus_button)
    back_button = types.InlineKeyboardButton("Назад", callback_data='menu')
    keyboard.row(back_button)
    return keyboard

@bot.message_handler(commands=['start'])
def handle_start(message):
    try:
        photo_path = 'img/LogoNeiroFood.jpg'
        bot.send_photo(message.chat.id, photo=open(photo_path, 'rb'), caption='Привет! Я ваш личный ассистент NeiroFood!', reply_markup=menu_tool_button())
        log(message)
    except Exception as e:
        printt(f"Ошибка при отправке изображения: {e}")
        logger.info(f'{e}')

@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.reply_to(message, f"Список доступных команд:\n\n{command_name(0)} - приветствие\n{command_name(1)} - справка")
    log(message)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    user_id = call.from_user.id
    if call.data.startswith('basket_'):
        action, burger_name = call.data.split('_')[1], call.data.split('_')[2]
        user_basket = get_user_basket(user_id)
        if action == "add":
            user_basket[burger_name] = user_basket.get(burger_name, 0) + 1
        elif action == "remove":
            if burger_name in user_basket:
                if user_basket[burger_name] > 1:
                    user_basket[burger_name] -= 1
                else:
                    del user_basket[burger_name]
        save_user_basket(user_id, user_basket)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=button_for_basket(burger_name, user_basket.get(burger_name, 0)))
        log(call, False, call.data)
    elif call.data == 'about':
        text = '''НейроФуд - сеть ресторанов, где блюда готовят высококлассные повара с помощью новейших технологий.'''
        bot.edit_message_text(text, call.message.chat.id, call.message.id, reply_markup=menu_tool_button())
        log(call, False, call.data)
    elif call.data == 'FAQ':
        text = '''Часто задаваемые вопросы:'''
        bot.edit_message_text(text, call.message.chat.id, call.message.id, reply_markup=menu_tool_button())
        log(call, False, call.data)
    elif call.data == 'menu':
        text = '''Меню'''
        photo_path = 'img/NeiroMenu.jpg'
        media = types.InputMediaPhoto(open(photo_path, "rb"), caption=text, parse_mode="Markdown")
        bot.edit_message_media(media, call.message.chat.id, call.message.id, reply_markup=menu_button())
        log(call, False, call.data)
    elif call.data == 'neiro_burger':
        text = '''Нейро-бургеры'''
        photo_path = 'img/NeiroBurger.png'
        media = types.InputMediaPhoto(open(photo_path, "rb"), caption=text, parse_mode="Markdown")
        bot.edit_message_media(media, call.message.chat.id, call.message.id, reply_markup=menu_neiro_burger())
        log(call, False, call.data)
    elif call.data == 'drinks':
        text = '''Напитки'''
        photo_path = 'img/NeiroDrinks.png'
        media = types.InputMediaPhoto(open(photo_path, "rb"), caption=text, parse_mode="Markdown")
        bot.edit_message_media(media, call.message.chat.id, call.message.id, reply_markup=back_button('back'))
        log(call, False, call.data)
    elif call.data == 'combo':
        text = '''Нейро-комбо'''
        photo_path = 'img/NeiroCombo.png'
        media = types.InputMediaPhoto(open(photo_path, "rb"), caption=text, parse_mode="Markdown")
        bot.edit_message_media(media, call.message.chat.id, call.message.id, reply_markup=back_button('back'))
        log(call, False, call.data)
    elif call.data == 'basket':
        text = display_basket(user_id)
        photo_path = 'img/LogoNeiroFood.jpg'
        media = types.InputMediaPhoto(open(photo_path, "rb"), caption=text, parse_mode="Markdown")
        bot.edit_message_media(media, call.message.chat.id, call.message.id, reply_markup=basket_button(user_id))
        log(call, False, call.data)
    elif call.data == 'back':
        text = '''Привет! Я ваш личный ассистент NeiroFood!'''
        photo_path = 'img/LogoNeiroFood.jpg'
        media = types.InputMediaPhoto(open(photo_path, "rb"), caption=text, parse_mode="Markdown")
        bot.edit_message_media(media, call.message.chat.id, call.message.id, reply_markup=menu_tool_button())
        log(call, False, call.data)
    else:
        if call.data in burgers:
            photo_path = f'img/burgers/{call.data}.png'
            media = types.InputMediaPhoto(open(photo_path, "rb"), caption=call.data, parse_mode="Markdown")
            quantity = get_user_basket(user_id).get(call.data, 0)
            bot.edit_message_media(media, call.message.chat.id, call.message.id, reply_markup=button_for_basket(call.data, quantity))
            log(call, False, call.data)

if __name__ == '__main__':
    try:
        on_ready()
        bot.polling()
    except Exception as e:
        printt(f"Ошибка при работе бота: {e}")
        logger.info(f"Ошибка при работе бота: {e}")
