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

# Словарь для хранения корзин пользователей
user_baskets = {}

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

def button_for_burger(burger_name, quantity=1):
    keyboard = types.InlineKeyboardMarkup()
    basket_button = types.InlineKeyboardButton(f"{quantity} шт. | В корзину", callback_data=f'basket_{burger_name}_add')
    minus_button = types.InlineKeyboardButton("-", callback_data=f'basket_{burger_name}_remove')
    plus_button = types.InlineKeyboardButton("+", callback_data=f'basket_{burger_name}_add')
    back_button = types.InlineKeyboardButton("Назад", callback_data='neiro_burger')
    keyboard.row(minus_button, basket_button, plus_button)
    keyboard.row(back_button)
    return keyboard

def menu_neiro_burger():
    keyboard = types.InlineKeyboardMarkup()
    button_angus_shef = types.InlineKeyboardButton("Ангус ШЕФ", callback_data='angus_shef')
    button_double_vopper = types.InlineKeyboardButton("Двойной ВОППЕР", callback_data='double_vopper')
    button_rodeo_burger = types.InlineKeyboardButton("Родео Бургер", callback_data='rodeo_burger')
    button_cesar_king = types.InlineKeyboardButton("Цезарь КИНГ", callback_data='cesar_king')
    button_censi = types.InlineKeyboardButton("ЦЭНСИ", callback_data='censi')
    button_bavarskii_burger = types.InlineKeyboardButton("Баварский бургер", callback_data='bavarskii_burger')
    button_black_mamba = types.InlineKeyboardButton("Черная МАМБА", callback_data='black_mamba')
    button_green_fresh = types.InlineKeyboardButton("Зеленный ФРЕШ", callback_data='green_fresh')
    button_double_cheeseburger = types.InlineKeyboardButton("Двойной Чизбургер", callback_data='double_cheeseburger')
    back_button = types.InlineKeyboardButton("Назад", callback_data='menu')
    keyboard.row(button_angus_shef)
    keyboard.row(button_double_vopper)
    keyboard.row(button_rodeo_burger)
    keyboard.row(button_cesar_king)
    keyboard.row(button_censi)
    keyboard.row(button_bavarskii_burger)
    keyboard.row(button_black_mamba)
    keyboard.row(button_green_fresh)
    keyboard.row(button_double_cheeseburger)
    keyboard.row(back_button)
    return keyboard

def display_basket(user_id):
    if user_id in user_baskets and user_baskets[user_id]:
        basket_text = "Ваша корзина:\n\n"
        for burger, quantity in user_baskets[user_id].items():
            basket_text += f"{burger}: {quantity} шт.\n"
        basket_text += "\nВы можете добавить или удалить бургеры."
    else:
        basket_text = "Ваша корзина пуста."
    return basket_text

def basket_button(user_id):
    keyboard = types.InlineKeyboardMarkup()
    if user_id in user_baskets:
        for burger, quantity in user_baskets[user_id].items():
            minus_button = types.InlineKeyboardButton(f"- {burger}", callback_data=f'basket_{burger}_remove')
            plus_button = types.InlineKeyboardButton(f"+ {burger}", callback_data=f'basket_{burger}_add')
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
        if user_id not in user_baskets:
            user_baskets[user_id] = {}
        if action == "add":
            if burger_name in user_baskets[user_id]:
                user_baskets[user_id][burger_name] += 1
            else:
                user_baskets[user_id][burger_name] = 1
        elif action == "remove":
            if burger_name in user_baskets[user_id]:
                if user_baskets[user_id][burger_name] > 1:
                    user_baskets[user_id][burger_name] -= 1
                else:
                    del user_baskets[user_id][burger_name]
        if action == "add":
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=button_for_burger(burger_name, user_baskets[user_id][burger_name]))
        elif action == "remove":
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=button_for_burger(burger_name, user_baskets[user_id].get(burger_name, 0)))
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
        photo_path = 'img/LogoNeiroFood.jpg'  # Вы можете заменить на подходящее изображение корзины
        media = types.InputMediaPhoto(open(photo_path, "rb"), caption=text, parse_mode="Markdown")
        bot.edit_message_media(media, call.message.chat.id, call.message.id, reply_markup=basket_button(user_id))
        log(call, False, call.data)
    elif call.data == 'angus_shef':
        text = '''Ангус ШЕФ'''
        photo_path = 'img/shef.png'
        media = types.InputMediaPhoto(open(photo_path, "rb"), caption=text, parse_mode="Markdown")
        quantity = user_baskets.get(user_id, {}).get('angus_shef', 1)
        bot.edit_message_media(media, call.message.chat.id, call.message.id, reply_markup=button_for_burger('angus_shef', quantity))
        log(call, False, call.data)
    elif call.data == 'double_vopper':
        text = '''Двойной ВОППЕР'''
        photo_path = 'img/vopper.png'
        media = types.InputMediaPhoto(open(photo_path, "rb"), caption=text, parse_mode="Markdown")
        quantity = user_baskets.get(user_id, {}).get('double_vopper', 1)
        bot.edit_message_media(media, call.message.chat.id, call.message.id, reply_markup=button_for_burger('double_vopper', quantity))    
        log(call, False, call.data)
    elif call.data == 'rodeo_burger':
        text = '''Родео Бургер'''
        photo_path = 'img/rodeo.png'
        media = types.InputMediaPhoto(open(photo_path, "rb"), caption=text, parse_mode="Markdown")
        quantity = user_baskets.get(user_id, {}).get('rodeo_burger', 1)
        bot.edit_message_media(media, call.message.chat.id, call.message.id, reply_markup=button_for_burger('rodeo_burger', quantity))
        log(call, False, call.data)
    elif call.data == 'cesar_king':
        text = '''Цезарь КИНГ'''
        photo_path = 'img/cesar.png'
        media = types.InputMediaPhoto(open(photo_path, "rb"), caption=text, parse_mode="Markdown")
        quantity = user_baskets.get(user_id, {}).get('cesar_king', 1)
        bot.edit_message_media(media, call.message.chat.id, call.message.id, reply_markup=button_for_burger('cesar_king', quantity))
        log(call, False, call.data)
    elif call.data == 'censi':
        text = '''ЦЭНСИ'''
        photo_path = 'img/censi.png'
        media = types.InputMediaPhoto(open(photo_path, "rb"), caption=text, parse_mode="Markdown")
        quantity = user_baskets.get(user_id, {}).get('censi', 1)
        bot.edit_message_media(media, call.message.chat.id, call.message.id, reply_markup=button_for_burger('censi', quantity))
        log(call, False, call.data)
    elif call.data == 'bavarskii_burger':
        text = '''Баварский бургер'''
        photo_path = 'img/bavarskii.png'
        media = types.InputMediaPhoto(open(photo_path, "rb"), caption=text, parse_mode="Markdown")
        quantity = user_baskets.get(user_id, {}).get('bavarskii_burger', 1)
        bot.edit_message_media(media, call.message.chat.id, call.message.id, reply_markup=button_for_burger('bavarskii_burger', quantity))     
        log(call, False, call.data)
    elif call.data == 'black_mamba':
        text = '''Черная МАМБА'''
        photo_path = 'img/mamba.png'
        media = types.InputMediaPhoto(open(photo_path, "rb"), caption=text, parse_mode="Markdown")
        quantity = user_baskets.get(user_id, {}).get('black_mamba', 1)
        bot.edit_message_media(media, call.message.chat.id, call.message.id, reply_markup=button_for_burger('black_mamba', quantity))        
        log(call, False, call.data)
    elif call.data == 'green_fresh':
        text = '''Зеленный ФРЕШ'''
        photo_path = 'img/fresh.png'
        media = types.InputMediaPhoto(open(photo_path, "rb"), caption=text, parse_mode="Markdown")
        quantity = user_baskets.get(user_id, {}).get('green_fresh', 1)
        bot.edit_message_media(media, call.message.chat.id, call.message.id, reply_markup=button_for_burger('green_fresh', quantity))    
        log(call, False, call.data)
    elif call.data == 'double_cheeseburger':
        text = '''Двойной Чизбургер'''
        photo_path = 'img/cheeseburger.png'
        media = types.InputMediaPhoto(open(photo_path, "rb"), caption=text, parse_mode="Markdown")
        quantity = user_baskets.get(user_id, {}).get('double_cheeseburger', 1)
        bot.edit_message_media(media, call.message.chat.id, call.message.id, reply_markup=button_for_burger('double_cheeseburger', quantity))
        log(call, False, call.data)
    elif call.data == 'back':
        text = '''Привет! Я ваш личный ассистент NeiroFood!'''
        photo_path = 'img/LogoNeiroFood.jpg'
        media = types.InputMediaPhoto(open(photo_path, "rb"), caption=text, parse_mode="Markdown")
        bot.edit_message_media(media, call.message.chat.id, call.message.id, reply_markup=menu_tool_button())
        log(call, False, call.data)


if __name__ == '__main__':
    try:
        on_ready()
        bot.polling()
    except Exception as e:
        printt(f"Ошибка при работе бота: {e}")
        logger.info(f"Ошибка при работе бота: {e}")
