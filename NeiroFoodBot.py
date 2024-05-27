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
def get_user_basket(user_id, username):
    username = username.replace(" ", "_")
    file_path = f'users/{user_id}_{username}.json'
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    else:
        return {}

def save_user_basket(user_id, username, basket):
    username = username.replace(" ", "_")
    file_path = f'users/{user_id}_{username}.json'
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

drinks = ['Coca-Cola',
          'Sprite',
          'Lipton',
          'КЛУБНИЧНЫЙ ШЕЙК',
          'ШОКОЛАДНЫЙ ШЕЙК',
          'ВАНИЛЬНЫЙ ШЕЙК']

combos = ['Шримп ВОППЕР',
         'Черная МАМБА',
         'Двойной ВОППЕР М',
         'Гамбургер Комбо',
         'Беконайзер Комбо',
         'Чизбургер Комбо']

deserts = ['Сырники',
           'Шоколадный Маффин',
           'Пирожок с вишней',
           'Карамельное мороженное',
           'Клубничное мороженное',
           'Пончики с кремом']

salads = ['Страчателла',
          'Салат греческий',
          'Салат Цезарь']

sous = ['Кетчуп',
        'Сырный',
        'Кисло-сладкий',
        'Чесночный',
        'Горчичный',
        'Барбекю']


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

def button_for_basket(item_name, quantity=1):
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    minus_button = types.InlineKeyboardButton("-", callback_data=f'basket_remove_{item_name}')
    basket_button = types.InlineKeyboardButton(f"{quantity} шт", callback_data='noop')
    plus_button = types.InlineKeyboardButton("+", callback_data=f'basket_add_{item_name}')
    back_button = types.InlineKeyboardButton("Назад", callback_data='neiro_burger')
    keyboard.add(minus_button, basket_button, plus_button)
    keyboard.row(back_button)
    return keyboard

def button_for_burger(item_name):
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
    button_basket = types.InlineKeyboardButton("Корзина", callback_data='basket')
    back_button = types.InlineKeyboardButton("Назад", callback_data='menu')
    keyboard.row(button_basket)
    keyboard.row(back_button)
    return keyboard

def menu_neiro_drinks():
    keyboard = types.InlineKeyboardMarkup()
    for drink in drinks:
        button = types.InlineKeyboardButton(drink, callback_data=drink)
        keyboard.row(button)
    button_basket = types.InlineKeyboardButton("Корзина", callback_data='basket')
    back_button = types.InlineKeyboardButton("Назад", callback_data='menu')
    keyboard.row(button_basket)
    keyboard.row(back_button)
    return keyboard

def menu_neiro_combo():
    keyboard = types.InlineKeyboardMarkup()
    for combo in combos:
        button = types.InlineKeyboardButton(combo, callback_data=combo)
        keyboard.row(button)
    button_basket = types.InlineKeyboardButton("Корзина", callback_data='basket')
    back_button = types.InlineKeyboardButton("Назад", callback_data='menu')
    keyboard.row(button_basket)
    keyboard.row(back_button)
    return keyboard

def menu_neiro_deserts():
    keyboard = types.InlineKeyboardMarkup()
    for desert in deserts:
        button = types.InlineKeyboardButton(desert, callback_data=deserts)
        keyboard.row(button)
    button_basket = types.InlineKeyboardButton("Корзина", callback_data='basket')
    back_button = types.InlineKeyboardButton("Назад", callback_data='menu')
    keyboard.row(button_basket)
    keyboard.row(back_button)
    return keyboard

def menu_neiro_salads():
    keyboard = types.InlineKeyboardMarkup()
    for salad in salads:
        button = types.InlineKeyboardButton(salad, callback_data=salad)
        keyboard.row(button)
    button_basket = types.InlineKeyboardButton("Корзина", callback_data='basket')
    back_button = types.InlineKeyboardButton("Назад", callback_data='menu')
    keyboard.row(button_basket)
    keyboard.row(back_button)
    return keyboard

def menu_neiro_sous():
    keyboard = types.InlineKeyboardMarkup()
    for souss in sous:
        button = types.InlineKeyboardButton(souss, callback_data=souss)
        keyboard.row(button)
    button_basket = types.InlineKeyboardButton("Корзина", callback_data='basket')
    back_button = types.InlineKeyboardButton("Назад", callback_data='menu')
    keyboard.row(button_basket)
    keyboard.row(back_button)
    return keyboard

def display_basket(user_id, username):
    user_basket = get_user_basket(user_id, username)
    if user_basket:
        basket_text = "Ваша корзина:\n\n"
        for item, quantity in user_basket.items():
            basket_text += f"{item}: {quantity} шт.\n"
        basket_text += "\nВы можете добавить или удалить бургеры."
    else:
        basket_text = "Ваша корзина пуста."
    return basket_text

def basket_button(user_id, username):
    keyboard = types.InlineKeyboardMarkup()
    user_basket = get_user_basket(user_id, username)
    if user_basket:
        for item, quantity in user_basket.items():
            burger_button = types.InlineKeyboardButton(f"{item}", callback_data=f'item_{item}')
            keyboard.row(burger_button)
    back_button = types.InlineKeyboardButton("Назад", callback_data='neiro_burger')
    keyboard.row(back_button)
    return keyboard

call_actions = [
    ('about', 'НейроФуд - сеть ресторанов, где блюда готовят высококлассные повара с помощью новейших технологий.', 'img/AboutNeiroFood.jpg', back_button('back')),
    ('FAQ', 'Часто задаваемые вопросы', 'img/FAQNeiroFood.jpg', back_button('back')),
    ('menu', 'Меню', 'img/NeiroMenu.jpg', menu_button()),
    ('neiro_burger', 'Нейро-бургеры', 'img/NeiroBurger.png', menu_neiro_burger()),
    ('drinks', 'Напитки', 'img/NeiroDrinks.png', menu_neiro_drinks()),
    ('combo', 'Нейро-комбо', 'img/NeiroCombo.png', menu_neiro_combo()),
    ('deserts', 'Десерты', 'img/NeiroCombo.png', menu_neiro_deserts()),
    ('salads', 'Салаты', 'img/NeiroCombo.png', menu_neiro_salads()),
    ('sous', 'Соусы', 'img/NeiroCombo.png', menu_neiro_sous()),
    ('back', 'Привет! Я ваш личный ассистент NeiroFood!', 'img/LogoNeiroFood.jpg', menu_tool_button())
]


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

# Обработка callback_query
@bot.callback_query_handler(func=lambda call: call.data in [action[0] for action in call_actions])
def handle_callback_query(call):
    user_id = call.from_user.id
    username = call.from_user.username
    for action in call_actions:
        if action[0] == call.data:
            text = action[1]
            photo_path = action[2]
            reply_markup = action[3]
            media = types.InputMediaPhoto(open(photo_path, "rb"), caption=text)
            bot.edit_message_media(media, call.message.chat.id, call.message.id, reply_markup=reply_markup)
            log(call, False, call.data)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    user_id = call.from_user.id
    username = call.from_user.username
    if call.data.startswith('basket_'):
        action, item_name = call.data.split('_')[1], call.data.split('_')[2]
        user_basket = get_user_basket(user_id, username)
        if action == "add":
            user_basket[item_name] = user_basket.get(item_name, 0) + 1
        elif action == "remove":
            if item_name in user_basket:
                if user_basket[item_name] > 1:
                    user_basket[item_name] -= 1
                else:
                    del user_basket[item_name]
        save_user_basket(user_id, username, user_basket)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=button_for_basket(item_name, user_basket.get(item_name, 0)))
        log(call, False, call.data)
    elif call.data.startswith('item_'):
        item_name = call.data.split('_')[1]
        quantity = get_user_basket(user_id, username).get(item_name, 0)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=button_for_basket(item_name, quantity))
        log(call, False, call.data)
    elif call.data == 'basket':
            text = display_basket(user_id, username)
            photo_path = 'img/LogoNeiroFood.jpg'
            media = types.InputMediaPhoto(open(photo_path, "rb"), caption=text)
            bot.edit_message_media(media, call.message.chat.id, call.message.id, reply_markup=basket_button(user_id, username))
            log(call, False, call.data)
    elif call.data == 'back':
        text = '''Привет! Я ваш личный ассистент NeiroFood!'''
        photo_path = 'img/LogoNeiroFood.jpg'
        media = types.InputMediaPhoto(open(photo_path, "rb"), caption=text)
        bot.edit_message_media(media, call.message.chat.id, call.message.id, reply_markup=menu_tool_button())
        log(call, False, call.data)
    else:
        if call.data in burgers:
            photo_path = f'img/burgers/{call.data}.png'
            media = types.InputMediaPhoto(open(photo_path, "rb"), caption=call.data)
            quantity = get_user_basket(user_id, username).get(call.data, 0)
            bot.edit_message_media(media, call.message.chat.id, call.message.id, reply_markup=button_for_basket(call.data, quantity))
            log(call, False, call.data)
        elif call.data in drinks:
            photo_path = f'img/drinks/{call.data}.png'
            media = types.InputMediaPhoto(open(photo_path, "rb"), caption=call.data)
            quantity = get_user_basket(user_id, username).get(call.data, 0)
            bot.edit_message_media(media, call.message.chat.id, call.message.id, reply_markup=button_for_basket(call.data, quantity))
            log(call, False, call.data)
        elif call.data in combos:
            photo_path = f'img/combos/{call.data}.png'
            media = types.InputMediaPhoto(open(photo_path, "rb"), caption=call.data)
            quantity = get_user_basket(user_id, username).get(call.data, 0)
            bot.edit_message_media(media, call.message.chat.id, call.message.id, reply_markup=button_for_basket(call.data, quantity))
            log(call, False, call.data)
        elif call.data in deserts:
            photo_path = f'img/deserts/{call.data}.png'
            media = types.InputMediaPhoto(open(photo_path, "rb"), caption=call.data)
            quantity = get_user_basket(user_id, username).get(call.data, 0)
            bot.edit_message_media(media, call.message.chat.id, call.message.id, reply_markup=button_for_basket(call.data, quantity))
            log(call, False, call.data)
        elif call.data in salads:
            photo_path = f'img/salads/{call.data}.png'
            media = types.InputMediaPhoto(open(photo_path, "rb"), caption=call.data)
            quantity = get_user_basket(user_id, username).get(call.data, 0)
            bot.edit_message_media(media, call.message.chat.id, call.message.id, reply_markup=button_for_basket(call.data, quantity))
            log(call, False, call.data)
        elif call.data in sous:
            photo_path = f'img/sous/{call.data}.png'
            media = types.InputMediaPhoto(open(photo_path, "rb"), caption=call.data)
            quantity = get_user_basket(user_id, username).get(call.data, 0)
            bot.edit_message_media(media, call.message.chat.id, call.message.id, reply_markup=button_for_basket(call.data, quantity))
            log(call, False, call.data)
         

if __name__ == '__main__':
    try:
        on_ready()
        bot.polling()
    except Exception as e:
        printt(f"Ошибка при работе бота: {e}")
        logger.info(f"Ошибка при работе бота: {e}")
