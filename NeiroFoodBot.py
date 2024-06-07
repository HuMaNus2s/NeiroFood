import os
import telebot
from telebot import types
import json
import logging
from datetime import datetime
import pytz
import time
from telebot.types import LabeledPrice
import random
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
rec_time = now.strftime("%d %B %Yг %H:%M")
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
    try:
        now = datetime.now(tz=moscow_tz)
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{current_time}] - {info}")
    except Exception as e:
        printt(f"Ошибка при оформлении logs: {e}")
        logger.info(f'{e}')
def on_ready():
    try:
        printt("BOT ACTIVATED!")
        logger.info('BOT ACTIVATED!')
    except Exception as e:
        printt(f"Бот аварийно прекратил работу: {e}")
        logger.info(f'{e}')
def log(message=None, error=False, button=None):
    try:
        if not error and not button:
            printt(f'{message.from_user.username} использовал команду <{message.text}>')
            logger.info(f'{message.from_user.username} использовал команду <{message.text}>')
        elif not error and button:
            printt(f'{message.from_user.username} использовал кнопку <{button}>')
            logger.info(f'{message.from_user.username} использовал кнопку <{button}>')
        else:
            printt(f'Неизвестная команда <{message.text}>')
            logger.info(f'Неизвестная команда <{message.text}>')
    except Exception as e:
        printt(f"Ошибка при формировании логов: {e}")
        logger.info(f'{e}')
# Работа с корзинами пользователей

def get_user_basket(user_id, username):
    try:
        if username is None:
            file_path = f'users/{user_id}.json'
        else:
            username = username.replace(" ", "_")
            file_path = f'users/{user_id}_{username}.json'
        
        # Проверка и создание каталога, если он не существует
        if not os.path.exists('users'):
            os.makedirs('users')

        # Если файл не существует, создаем его с пустым содержимым
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump({}, file, ensure_ascii=False, indent=4)
        
        # Чтение содержимого файла
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        printt(f"Ошибка при чтении json файла {user_id}_{username}: {e}")
        logger.info(f'{e}')
        return {}

def save_user_basket(user_id, username, basket):
    try:
        if username is None:
            file_path = f'users/{user_id}.json'
        else:
            username = username.replace(" ", "_")
            file_path = f'users/{user_id}_{username}.json'
        if not os.path.exists('users'):
            os.makedirs('users')
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(basket, file, ensure_ascii=False, indent=4)
    except Exception as e:
        printt(f"Ошибка при сохранении json файла {user_id}_{username}: {e}")
        logger.info(f'{e}')

def clear_user_basket(user_id, username):
    try:
        if username is None:
            file_path = f'users/{user_id}.json'
        else:
            username = username.replace(" ", "_")
            file_path = f'users/{user_id}_{username}.json'
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        printt(f"Ошибка при удалении json файла {user_id}_{username}: {e}")
        logger.info(f'{e}')

def clear_item_in_basket(user_id, username, item_name):
    try:
        if username is None:
            file_path = f'users/{user_id}.json'
        else:
            username = username.replace(" ", "_")
            file_path = f'users/{user_id}_{username}.json'
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        # Удаление элемента, если он присутствует
        if item_name in data:
            del data[item_name]
            print(f"{username} удалил товар '{item_name}' из корзины.")
        else:
            print(f"{username}, элемент '{item_name}' не найден в корзине.")

        # Запись обновленного содержимого обратно в файл с указанием кодировки UTF-8
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
    except Exception as e:
        printt(f"Ошибка при удалении {item_name} из корзины {user_id}_{username}: {e}")
        logger.info(f'{e}')

burgers = [
    ('Ангус ШЕФ', 150, 'Сочный бургер с котлетой из говядины Ангус, свежими овощами и фирменным соусом.'),
    ('Двойной ВОППЕР', 150, 'Двойное удовольствие от двух котлет и свежих овощей, с оригинальным соусом.'),
    ('Родео Бургер', 150, 'Бургер с кольцами лука, барбекю соусом и хрустящим беконом.'),
    ('Цезарь КИНГ', 150, 'Бургер с курицей, сыром пармезан, свежими овощами и соусом цезарь.'),
    ('ЦЭНСИ', 150, 'Бургер с котлетой из свинины, сыром и острым соусом.'),
    ('Баварский бургер', 150, 'Бургер с баварской колбаской, квашеной капустой и горчичным соусом.'),
    ('Черная МАМБА', 150, 'Экзотический бургер с черной булочкой, котлетой из говядины и острым соусом.'),
    ('Зеленный ФРЕШ', 150, 'Вегетарианский бургер с овощами и сыром тофу.'),
    ('Двойной Чизбургер', 150, 'Классический чизбургер с двойным количеством сыра и котлет.'),
]

drinks = [
    ('Coca-Cola', 100, 'Освежающий напиток Coca-Cola.'),
    ('Sprite', 100, 'Лимонад Sprite с легким лимонным вкусом.'),
    ('Lipton', 90, 'Чай Lipton со вкусом лимона.'),
    ('КЛУБНИЧНЫЙ ШЕЙК', 150, 'Сладкий молочный коктейль с клубничным вкусом.'),
    ('ШОКОЛАДНЫЙ ШЕЙК', 150, 'Молочный коктейль с насыщенным шоколадным вкусом.'),
    ('ВАНИЛЬНЫЙ ШЕЙК', 150, 'Молочный коктейль с нежным ванильным вкусом.'),
]
combos = [
    ('Шримп ВОППЕР', 180, 'Комбо с бургером из креветок, картошкой фри и напитком.'),
    ('Черная МАМБА', 200, 'Комбо с бургером "Черная МАМБА", картошкой фри и напитком.'),
    ('Двойной ВОППЕР М', 200, 'Комбо с двойным ВОППЕРом, картошкой фри и напитком.'),
    ('Гамбургер Комбо', 250, 'Комбо с гамбургером, картошкой фри и напитком.'),
    ('Беконайзер Комбо', 180, 'Комбо с бургером "Беконайзер", картошкой фри и напитком.'),
    ('Чизбургер Комбо', 210, 'Комбо с чизбургером, картошкой фри и напитком.'),
]
deserts = [
    ('Сырники', 70, 'Нежные сырники со сметаной и вареньем.'),
    ('Шоколадный Маффин', 50, 'Маффин с насыщенным шоколадным вкусом.'),
    ('Пирожок с вишней', 70, 'Сладкий пирожок с начинкой из вишни.'),
    ('Карамельное мороженное', 80, 'Мороженное с карамельным соусом.'),
    ('Клубничное мороженное', 80, 'Мороженное с клубничным соусом.'),
    ('Пончики с кремом', 80, 'Пончики с нежным кремом.'),
]
salads = [
    ('Страчателла', 120, 'Салат с сыром страчателла и свежими овощами.'),
    ('Салат греческий', 120, 'Классический греческий салат с фетой и оливками.'),
    ('Салат Цезарь', 150, 'Салат "Цезарь" с курицей, пармезаном и соусом цезарь.'),
]
sous = [
    ('Кетчуп', 50, 'Томатный соус кетчуп.'),
    ('Сырный', 50, 'Сырный соус.'),
    ('Кисло-сладкий', 60, 'Кисло-сладкий соус.'),
    ('Чесночный', 60, 'Соус с насыщенным чесночным вкусом.'),
    ('Горчичный', 40, 'Горчичный соус.'),
    ('Барбекю', 70, 'Соус барбекю с дымком.'),
]

def button(name, callback):
    try:
        return types.InlineKeyboardButton(name, callback_data=callback)
    except Exception as e:
        printt(f"Ошибка при создании кнопки {name} ведущую в {callback}: {e}")
        logger.info(f'{e}')

def back_button(call):
    try:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.row(button("Назад",call))
        return keyboard
    except Exception as e:
        printt(f"Ошибка возвращении в {call}: {e}")
        logger.info(f'{e}')
def menu_tool_button():
    try:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.row(button("О нас", "about"), button("FAQ", "FAQ"))
        keyboard.row(button("Меню", "menu"), button("Корзина", "basket"))
        return keyboard
    except Exception as e:
        printt(f"Неудалось создать кнопки главного меню: {e}")
        logger.info(f'{e}')
def menu_button():
    try:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.row(button("Нейро-бургеры","neiro_burger"))
        keyboard.row(button("Напитки","drinks"))
        keyboard.row(button("Нейро-комбо","combo"))
        keyboard.row(button("Десерты","deserts"))
        keyboard.row(button("Салаты","salads"))
        keyboard.row(button("Соусы","sous"))
        keyboard.row(button("Корзина","basket"))
        keyboard.row(button("Назад","back"))
        return keyboard
    except Exception as e:
        printt(f"Ошибка при создании меню: {e}")
        logger.info(f'{e}')

def button_for_basket(item_name, quantity=1):
    try:
        category, price, _ = find_category_and_price(item_name)
        # Проверка цены на None
        if price is None:
            raise ValueError(f"'{item_name}' не имеет цены. Добавить.")
        keyboard = types.InlineKeyboardMarkup(row_width=3)
        keyboard.row(button(f"{item_name} - {price} руб", "basket"))
        keyboard.add(button("-", f"basket_remove_{item_name}"),
                     button(f"{quantity} шт - {price * quantity} руб", "basket"),
                     button("+", f"basket_add_{item_name}"))
        keyboard.row(button("Ещё товары", "menu"),button("Оформить покупку", f"buy_{item_name}"), button("Корзина", "basket"))
        keyboard.add(button("Удалить из корзины", f"clear_item_in_basket_{item_name}"), button("Назад", "basket")) 
        return keyboard
    except Exception as e:
        printt(f"Ошибка при создании позиции товара: {e}")
        logger.info(f'{e}')

def menu_neiro_burger():
    try:
        keyboard = types.InlineKeyboardMarkup()
        for burger in burgers:
            keyboard.row(button(burger[0],burger[0]))
        keyboard.row(button("Корзина","basket"))
        keyboard.row(button("Назад","menu"))
        return keyboard
    except Exception as e:
        printt(f"Ошибка при создании меню бургеров: {e}")
        logger.info(f'{e}')
def menu_neiro_drinks():
    try:
        keyboard = types.InlineKeyboardMarkup()
        for drink in drinks:
            keyboard.row(button(drink[0],drink[0]))
        keyboard.row(button("Корзина","basket"))
        keyboard.row(button("Назад","menu"))
        return keyboard
    except Exception as e:
        printt(f"Ошибка при создании меню напитков: {e}")
        logger.info(f'{e}')
def menu_neiro_combo():
    try:
        keyboard = types.InlineKeyboardMarkup()
        for combo in combos:
            keyboard.row(button(combo[0],combo[0]))
        keyboard.row(button("Корзина","basket"))
        keyboard.row(button("Назад","menu"))
        return keyboard
    except Exception as e:
        printt(f"Ошибка при создании меню комбо: {e}")
        logger.info(f'{e}')
def menu_neiro_deserts():
    try:
        keyboard = types.InlineKeyboardMarkup()
        for desert in deserts:
            keyboard.row(button(desert[0],desert[0]))
        keyboard.row(button("Корзина","basket"))
        keyboard.row(button("Назад","menu"))
        return keyboard
    except Exception as e:
        printt(f"Ошибка при создании меню десертов: {e}")
        logger.info(f'{e}')
def menu_neiro_salads():
    try:
        keyboard = types.InlineKeyboardMarkup()
        for salad in salads:
            keyboard.row(button(salad[0],salad[0]))
        keyboard.row(button("Корзина","basket"))
        keyboard.row(button("Назад","menu"))
        return keyboard
    except Exception as e:
        printt(f"Ошибка при создании меню салатов: {e}")
        logger.info(f'{e}')
def menu_neiro_sous():
    try:
        keyboard = types.InlineKeyboardMarkup()
        for souss in sous:
            keyboard.row(button(souss[0],souss[0]))
        keyboard.row(button("Корзина","basket"))
        keyboard.row(button("Назад","menu"))
        return keyboard
    except Exception as e:
        printt(f"Ошибка при создании меню соусов: {e}")
        logger.info(f'{e}')

def display_basket(user_id, username):
    try:
        user_basket = get_user_basket(user_id, username)
        total_cost = 0
        if user_basket:
            basket_text = "*Ваша корзина:*\n\n"
            for item, quantity in user_basket.items():
                category, price, _ = find_category_and_price(item)
                if price is None:
                    print(f"Error: Price for item '{item}' is None")
                    continue
                item_cost = price * quantity
                total_cost += item_cost
                basket_text += f"*{item}: {item_cost} руб* | ({quantity} шт x {price} руб)\n"
            basket_text += f"\nОбщая стоимость: *{total_cost} руб*"
            basket_text += "\nВы можете добавить или удалить товары."
        else:
            basket_text = "*Ваша корзина пуста.*"
        return basket_text
    except Exception as e:
        printt(f"Ошибка при создании или чтении корзины: {e}")
        logger.info(f'{e}')

def basket_button(user_id, username):
    try:
        keyboard = types.InlineKeyboardMarkup(row_width=3)
        user_basket = get_user_basket(user_id, username)
        if user_basket:
            for item, quantity in user_basket.items():
                item_safe = item.replace(' ', '_')
                keyboard.row(button(f"{item}", f"item_{item_safe}"))
            keyboard.row(button("Добавить товары в корзину", "menu"))
            keyboard.row(button("Оформить заказ", "buy_all"))
            keyboard.add(button("Очистить корзину", "clear_basket"), button("Назад", "menu"))
        else:
            keyboard.row(button("Добавить товары в корзину", "menu"))
            keyboard.row(button("Назад", "back"))
        return keyboard
    except Exception as e:
        printt(f"Ошибка при создании кнопок корзины: {e}")
        logger.info(f'{e}')


def find_category_and_price(call_data):
    try:
        all_categories = {
            'burgers': burgers,
            'drinks': drinks,
            'combos': combos,
            'deserts': deserts,
            'salads': salads,
            'sous': sous
        }
        for category_name, items in all_categories.items():
            for item_name, price, description in items:
                if item_name == call_data:
                    return category_name, price, description
        return None, None, None
    except Exception as e:
        printt(f"Ошибка при поиске категории, цены или описания: {e}")
        logger.info(f'{e}')

call_actions = [
    ('about', '''*NeiroFood*
🍵В ᴄᴀʍᴏʍ ᴄᴇᴩдцᴇ ᴛᴇхнᴏᴧᴏᴦичᴇᴄᴋᴏᴦᴏ ᴋʙᴀᴩᴛᴀᴧᴀ, ᴦдᴇ иᴄᴋуᴄᴄᴛʙᴏ ᴨᴩᴏᴦᴩᴀʍʍиᴩᴏʙᴀния ᴄᴏᴇдиняᴇᴛᴄя ᴄ ᴋуᴧинᴀᴩныʍ иᴄᴋуᴄᴄᴛʙᴏʍ, ᴩᴀᴄᴨᴏᴧᴏжиᴧᴏᴄь униᴋᴀᴧьнᴏᴇ ɜᴀʙᴇдᴇниᴇ - NeiroFood.

🍵Здᴇᴄь ᴦᴏᴄᴛи ᴨᴏᴦᴩужᴀюᴛᴄя ʙ ʍиᴩ иннᴏʙᴀций, ᴦдᴇ нᴇᴏбычныᴇ бᴧюдᴀ ᴄᴏɜдᴀюᴛᴄя бᴧᴀᴦᴏдᴀᴩя иᴄᴋуᴄᴄᴛʙᴇннᴏʍу инᴛᴇᴧᴧᴇᴋᴛу. Гᴩуᴨᴨᴀ ᴛᴀᴧᴀнᴛᴧиʙых ᴄᴛудᴇнᴛᴏʙ-ᴨᴩᴏᴦᴩᴀʍʍиᴄᴛᴏʙ ᴨᴩᴇʙᴩᴀᴛиᴧᴀ ᴄʙᴏи ɜнᴀния ʙ ᴋуᴧинᴀᴩнᴏᴇ ᴨᴩиᴋᴧючᴇниᴇ, ᴦдᴇ ᴋᴀждый ɜᴀᴋᴀɜ - ϶ᴛᴏ униᴋᴀᴧьнᴏᴇ ᴛʙᴏᴩᴇниᴇ ʍᴀɯинного ᴩᴀɜуʍᴀ.

🍵В нᴇйᴩᴏᴋᴀɸᴇ ᴋᴀждый ᴨᴏᴄᴇᴛиᴛᴇᴧь ᴄᴛᴀнᴏʙиᴛᴄя учᴀᴄᴛниᴋᴏʍ ϶ᴋᴄᴨᴇᴩиʍᴇнᴛᴀ, ᴨᴏɜʙᴏᴧяя иᴄᴋуᴄᴄᴛʙᴇннᴏʍу инᴛᴇᴧᴧᴇᴋᴛу ᴩᴀᴄᴋᴩыᴛь ᴇᴦᴏ ᴨᴩᴇдᴨᴏчᴛᴇния и ᴄᴏɜдᴀᴛь идᴇᴀᴧьнᴏᴇ бᴧюдᴏ. Эᴛᴏ ʍᴇᴄᴛᴏ, ᴦдᴇ ᴛᴇхнᴏᴧᴏᴦии ʙᴄᴛᴩᴇчᴀюᴛᴄя ᴄ ᴦᴀᴄᴛᴩᴏнᴏʍиᴇй, и ʙᴏᴧɯᴇбᴄᴛʙᴏ ᴨᴩᴏиᴄхᴏдиᴛ нᴀ ᴋᴀждᴏй ᴛᴀᴩᴇᴧᴋᴇ.
''', 'img/AboutNeiroFood.jpg', back_button('back')),
    ('FAQ', '''*1. Что такое "NeiroFood"?*  
*NeiroFood* - бургерная 🍔, созданная студентами курса Интернет-Маркетинга. Мы используем нейросети для создания уникальных рецептов бургеров.  
*2. Как я могу ознакомиться с вашим меню?*  
Меню доступно в нашем телеграм-боте, нажмите кнопку "Меню".  
*3. Как я могу сделать заказ?*  
Выберите бургер из меню и следуйте инструкциям бота. Мы доставим ваш заказ в кратчайшие сроки.  
*4. Какие способы оплаты вы принимаете?*  
Оплата наличными и через онлайн-платформы (карты, электронные кошельки).  
*5. Есть ли у вас программы лояльности или скидки?*  
Сейчас программ лояльности нет, но мы работаем над этим. Следите за обновлениями в телеграм-канале или приложении.  
*6. Как я могу связаться с вашей поддержкой?*  
Напишите через телеграм-бота или позвоните по указанному номеру телефона, также у нас есть сайт.  
*7. Какие часы работы у вас?*  
Мы работаем ежедневно с _9:00_ до _15:50_.''', 'img/FAQNeiroFood.jpg', back_button('back')),
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
    try:
        bot.reply_to(message, f"Список доступных команд:\n\n{command_name(0)} - приветствие\n{command_name(1)} - справка")
        log(message)
    except Exception as e:
        printt(f"Ошибка при использовании команды help: {e}")
        logger.info(f'{e}')
# Обработка callback_query
@bot.callback_query_handler(func=lambda call: call.data in [action[0] for action in call_actions])
def handle_callback_query(call):
    try:
        user_id = call.from_user.id
        username = call.from_user.username
        for action in call_actions:
            if action[0] == call.data:
                text = action[1]
                photo_path = action[2]
                reply_markup = action[3]
                media = types.InputMediaPhoto(open(photo_path, "rb"), caption=text, parse_mode="Markdown")
                bot.edit_message_media(media, call.message.chat.id, call.message.id, reply_markup=reply_markup)
                log(call, False, call.data)
    except Exception as e:
        printt(f"Ошибка вызова {call}: {e}")
        logger.info(f'{e}')
@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    try:
        user_id = call.from_user.id
        username = call.from_user.username
        category, price, description = find_category_and_price(call.data)
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
            item_name = call.data.split('_',1)[1].replace("_"," ")
            quantity = get_user_basket(user_id, username).get(item_name, 0)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=button_for_basket(item_name, quantity))
            log(call, False, call.data)

        elif call.data == 'basket':
            text = display_basket(user_id, username)
            photo_path = 'img/LogoNeiroFood.jpg'
            media = types.InputMediaPhoto(open(photo_path, "rb"), caption=text, parse_mode="Markdown")
            bot.edit_message_media(media, call.message.chat.id, call.message.id, reply_markup=basket_button(user_id, username))
            log(call, False, call.data)

        elif call.data == 'clear_basket':
            clear_user_basket(user_id, username)
            text = "*Ваша корзина была очищена.*"
            photo_path = 'img/LogoNeiroFood.jpg'
            print(basket_button(user_id, username))
            media = types.InputMediaPhoto(open(photo_path, "rb"), caption=text, parse_mode="Markdown")
            bot.edit_message_media(media, call.message.chat.id, call.message.id, reply_markup=basket_button(user_id, username))
            log(call, False, call.data)
        elif call.data.startswith('clear_item_in_basket_'):
            item_name = call.data.split('_', 4)[4].replace('_', ' ')
            clear_item_in_basket(user_id, username, item_name)
            text = f"*Товар {item_name} был удалён из корзины*"
            photo_path = 'img/LogoNeiroFood.jpg'
            print(basket_button(user_id, username))
            media = types.InputMediaPhoto(open(photo_path, "rb"), caption=text, parse_mode="Markdown")
            bot.edit_message_media(media, call.message.chat.id, call.message.id, reply_markup=basket_button(user_id, username))
            log(call, False, call.data)

        elif call.data == 'back':
            text = '''Привет! Я ваш личный ассистент NeiroFood!'''
            photo_path = 'img/LogoNeiroFood.jpg'
            media = types.InputMediaPhoto(open(photo_path, "rb"), caption=text, parse_mode="Markdown")
            bot.edit_message_media(media, call.message.chat.id, call.message.id, reply_markup=menu_tool_button())
            log(call, False, call.data)
            
        if call.data == "buy_all":
            user_basket = get_user_basket(user_id, username)
            if user_basket:
                prices = [LabeledPrice(label=item_name, amount=price*quantity*100) for item_name, quantity in user_basket.items() for category, price, _ in [find_category_and_price(item_name)]]
                bot.send_invoice(
                    chat_id=call.message.chat.id,
                    title="NeiroFood",
                    description=f"Номер заказа: {str(random.randint(0, 9999)).zfill(4)} | {rec_time}",
                    provider_token=config['payments_token'],
                    currency="RUB",
                    prices=prices,
                    start_parameter="time-machine-example",
                    invoice_payload="basket_purchase"
                )
                bot.delete_message(call.message.chat.id, call.message.message_id)
            else:
                bot.answer_callback_query(call.id, "Ваша корзина пуста.")
            log(call, False, call.data)
            return
        if call.data.startswith("buy_"):
            item_name = call.data.split("_", 1)[1]
            user_basket = get_user_basket(user_id, username)
            if item_name in user_basket:
                item = user_basket[item_name]
                quantity = user_basket[item_name]
                category, price, _ = find_category_and_price(item_name)
                labeled_price = LabeledPrice(label=item_name, amount=price * quantity * 100)
                bot.send_invoice(
                    chat_id=call.message.chat.id,
                    title="NeiroFood",
                    description=f"Покупка {item_name}",
                    provider_token=config['payments_token'],
                    currency="RUB",
                    prices=[labeled_price],
                    start_parameter="time-machine-example",
                    invoice_payload=f"item_purchase_{item_name}"
                )
                bot.delete_message(call.message.chat.id, call.message.message_id)
            else:
                bot.answer_callback_query(call.id, "Товар не найден в корзине.")
            log(call, False, call.data)
            return

        if category:
            photo_path = f'img/{category}/{call.data}.png'
            try:
                media = types.InputMediaPhoto(open(photo_path, "rb"), caption=f"*{call.data}*:\n{description}", parse_mode="Markdown")
                quantity = get_user_basket(user_id, username).get(call.data, 0)
                bot.edit_message_media(media, call.message.chat.id, call.message.id, reply_markup=button_for_basket(call.data, quantity))
                log(call, False, call.data)
            except Exception as e:
                print(f"Ошибка при открытии файла: {e}")
        else:
            pass  
    except Exception as e:
        printt(f"Ошибка: {e}")
        logger.info(f'{e}')
# Обработчик успешной оплаты
@bot.pre_checkout_query_handler(func=lambda query: True)
def process_pre_checkout_query(pre_checkout_query):
    try:
        bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
    except Exception as e:
        printt(f"Ошибка при обработке оплаты: {e}")
        logger.info(f'{e}')

@bot.message_handler(content_types=['successful_payment'])
def process_successful_payment(message):
    try:
        payload = message.successful_payment.invoice_payload
        user_id = message.from_user.id
        username = message.from_user.username
        
        if payload == "basket_purchase":
            handle_start(message)
            clear_user_basket(user_id, username)
        elif payload.startswith("item_purchase_"):
            item_id = payload.split("_")[2]
            handle_start(message)
            clear_item_in_basket(user_id, username, item_id)
        log(message, True, payload)
    except Exception as e:
        printt(f"Ошибка при постобработке заказа: {e}")
        logger.info(f'{e}')
    
if __name__ == '__main__':
    try:
        on_ready()
        bot.polling()
    except Exception as e:
        printt(f"Ошибка при работе бота: {e}")
        logger.info(f"Ошибка при работе бота: {e}")
