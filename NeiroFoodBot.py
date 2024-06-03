
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

categories = {
    'burgers':{'Ангус ШЕФ': 180, 'Двойной ВОППЕР': 200, 'Родео Бургер': 120, 'Цезарь КИНГ': 200, 'ЦЭНСИ': 200, 'Баварский бургер': 200, 'Черная МАМБА': 150, 'Зеленный ФРЕШ': 250, 'Двойной Чизбургер': 100},
    'drinks': {'Coca-Cola': 100, 'Sprite': 80, 'Lipton': 150, 'КЛУБНИЧНЫЙ ШЕЙК': 170, 'ШОКОЛАДНЫЙ ШЕЙК': 200, 'ВАНИЛЬНЫЙ ШЕЙК': 150},
    'combos': {'Шримп ВОППЕР': 200, 'Черная МАМБА': 200, 'Двойной ВОППЕР М': 200, 'Гамбургер Комбо': 200, 'Беконайзер Комбо': 200, 'Чизбургер Комбо': 200},
    'deserts':{'Сырники': 100, 'Шоколадный Маффин': 50, 'Пирожок с вишней': 70, 'Карамельное мороженное': 150, 'Клубничное мороженное': 100, 'Пончики с кремом': 60},
    'salads': {'Страчателла': 100, 'Салат греческий': 170, 'Салат Цезарь': 200},
    'sous':   {'Кетчуп': 50, 'Сырный': 50, 'Кисло-сладкий': 60, 'Чесночный': 70, 'Горчичный': 60, 'Барбекю': 70}
}

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
    rus_name_menu = ["Нейро-бургеры","Напитки","Нейро-комбо","Десерты","Салаты","Соусы"]
    for category in rus_name_menu:
        button = types.InlineKeyboardButton(category, callback_data=category.lower())
        keyboard.row(button)
    back_button = types.InlineKeyboardButton("Назад", callback_data='back')
    keyboard.row(back_button)
    return keyboard

# Обновление кнопок для каждого товара
def button_for_basket(item_name, quantity=1):
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    minus_button = types.InlineKeyboardButton("-", callback_data=f'basket_remove_{item_name}')
    basket_button = types.InlineKeyboardButton(f"{quantity} шт - {burger_prices[item_name] * quantity} руб.", callback_data='basket')
    plus_button = types.InlineKeyboardButton("+", callback_data=f'basket_add_{item_name}')
    back_button = types.InlineKeyboardButton("Назад", callback_data='menu')
    keyboard.add(minus_button, basket_button, plus_button)
    keyboard.row(back_button)
    return keyboard

def menu_neiro_burger():
    keyboard = types.InlineKeyboardMarkup()
    for burger, price in categories['burgers'].items():
        button = types.InlineKeyboardButton(f"{burger} - {price} руб.", callback_data=burger)
        keyboard.row(button)
    button_basket = types.InlineKeyboardButton("Корзина", callback_data='basket')
    back_button = types.InlineKeyboardButton("Назад", callback_data='menu')
    keyboard.row(button_basket)
    keyboard.row(back_button)
    return keyboard

def menu_neiro_drinks():
    keyboard = types.InlineKeyboardMarkup()
    for drink, price in categories['drinks'].items():
        button = types.InlineKeyboardButton(f"{drink} - {price} руб.", callback_data=drink)
        keyboard.row(button)
    button_basket = types.InlineKeyboardButton("Корзина", callback_data='basket')
    back_button = types.InlineKeyboardButton("Назад", callback_data='menu')
    keyboard.row(button_basket)
    keyboard.row(back_button)
    return keyboard

def menu_neiro_combo():
    keyboard = types.InlineKeyboardMarkup()
    for combo, price in categories['combos'].items():
        button = types.InlineKeyboardButton(f"{combo} - {price} руб.", callback_data=combo)
        keyboard.row(button)
    button_basket = types.InlineKeyboardButton("Корзина", callback_data='basket')
    back_button = types.InlineKeyboardButton("Назад", callback_data='menu')
    keyboard.row(button_basket)
    keyboard.row(back_button)
    return keyboard

def menu_neiro_deserts():
    keyboard = types.InlineKeyboardMarkup()
    for desert, price in categories['deserts'].items():
        button = types.InlineKeyboardButton(f"{desert} - {price} руб.", callback_data=desert)
        keyboard.row(button)
    button_basket = types.InlineKeyboardButton("Корзина", callback_data='basket')
    back_button = types.InlineKeyboardButton("Назад", callback_data='menu')
    keyboard.row(button_basket)
    keyboard.row(back_button)
    return keyboard

def menu_neiro_salads():
    keyboard = types.InlineKeyboardMarkup()
    for salad, price in categories['salads'].items():
        button = types.InlineKeyboardButton(f"{salad} - {price} руб.", callback_data=salad)
        keyboard.row(button)
    button_basket = types.InlineKeyboardButton("Корзина", callback_data='basket')
    back_button = types.InlineKeyboardButton("Назад", callback_data='menu')
    keyboard.row(button_basket)
    keyboard.row(back_button)
    return keyboard

def menu_neiro_sous():
    keyboard = types.InlineKeyboardMarkup()
    for souss, price in categories['sous'].items():
        button = types.InlineKeyboardButton(f"{souss} - {price} руб.", callback_data=souss)
        keyboard.row(button)
    button_basket = types.InlineKeyboardButton("Корзина", callback_data='basket')
    back_button = types.InlineKeyboardButton("Назад", callback_data='menu')
    keyboard.row(button_basket)
    keyboard.row(back_button)
    return keyboard


def display_basket(user_id, username, category):
    user_basket = get_user_basket(user_id, username)
    if user_basket:
        basket_text = "Ваша корзина:\n\n"
        for item, quantity in user_basket.items():
            price = categories[category][item]
            basket_text += f"{item}: {quantity} шт. - {price} руб.| {price*quantity} руб.\n"
        basket_text += "\nВы можете добавить или удалить товары."
    else:
        basket_text = "Ваша корзина пуста."
    return basket_text


def basket_button(user_id, username):
    keyboard = types.InlineKeyboardMarkup()
    user_basket = get_user_basket(user_id, username)
    if user_basket:
        for item, quantity in user_basket.items():
            item_button = types.InlineKeyboardButton(f"{item}", callback_data=f'item_{item}')
            keyboard.row(item_button)
    back_button = types.InlineKeyboardButton("Назад", callback_data='menu')
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
    elif call.data in categories['burgers']:
        photo_path = f'img/burgers/{call.data}.png'
        media = types.InputMediaPhoto(open(photo_path, "rb"), caption=call.data)
        quantity = get_user_basket(user_id, username).get(call.data, 0)
        bot.edit_message_media(media, call.message.chat.id, call.message.id, reply_markup=button_for_basket(call.data, quantity))
        log(call, False, call.data)
    elif call.data in categories['drinks']:
        photo_path = f'img/drinks/{call.data}.png'
        media = types.InputMediaPhoto(open(photo_path, "rb"), caption=call.data)
        quantity = get_user_basket(user_id, username).get(call.data, 0)
        bot.edit_message_media(media, call.message.chat.id, call.message.id, reply_markup=button_for_basket(call.data, quantity))
        log(call, False, call.data)
    elif call.data in categories['combos']:
        photo_path = f'img/combos/{call.data}.png'
        media = types.InputMediaPhoto(open(photo_path, "rb"), caption=call.data)
        quantity = get_user_basket(user_id, username).get(call.data, 0)
        bot.edit_message_media(media, call.message.chat.id, call.message.id, reply_markup=button_for_basket(call.data, quantity))
        log(call, False, call.data)
    elif call.data in categories['deserts']:
        photo_path = f'img/deserts/{call.data}.png'
        media = types.InputMediaPhoto(open(photo_path, "rb"), caption=call.data)
        quantity = get_user_basket(user_id, username).get(call.data, 0)
        bot.edit_message_media(media, call.message.chat.id, call.message.id, reply_markup=button_for_basket(call.data, quantity))
        log(call, False, call.data)
    elif call.data in categories['salads']:
        photo_path = f'img/salads/{call.data}.png'
        media = types.InputMediaPhoto(open(photo_path, "rb"), caption=call.data)
        quantity = get_user_basket(user_id, username).get(call.data, 0)
        bot.edit_message_media(media, call.message.chat.id, call.message.id, reply_markup=button_for_basket(call.data, quantity))
        log(call, False, call.data)
    elif call.data in categories['sous']:
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
