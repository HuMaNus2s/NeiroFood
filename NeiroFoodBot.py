import os
import telebot
from telebot import types
import json
import logging
from datetime import datetime
import pytz
import time
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

def clear_user_basket(user_id, username):
    username = username.replace(" ", "_")
    file_path = f'users/{user_id}_{username}.json'
    if os.path.exists(file_path):
        os.remove(file_path)
def clear_item_in_basket(user_id, username, item_name):
    # Подготовка имени пользователя для использования в качестве части имени файла
    username = username.replace(" ", "_")
    file_path = f'users/{user_id}_{username}.json'
    
    # Проверка наличия файла корзины пользователя
    if os.path.exists(file_path):
        # Загрузка корзины пользователя из файла JSON
        with open(file_path, 'r') as file:
            user_basket = json.load(file)
        
        # Удаление указанного товара из корзины, если он там есть
        if item_name in user_basket:
            del user_basket[item_name]
        
        # Сохранение обновленной корзины обратно в файл JSON
        with open(file_path, 'w') as file:
            json.dump(user_basket, file)
    else:
        print("Файл корзины не найден.")
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
    return types.InlineKeyboardButton(name, callback_data=callback)

def back_button(call):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(button("Назад",call))
    return keyboard
def menu_tool_button():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(button("О нас", "about"), button("FAQ", "FAQ"))
    keyboard.row(button("Меню", "menu"), button("Корзина", "basket"))
    return keyboard
def menu_button():
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

def button_for_basket(item_name, quantity=1):
    category, price, _ = find_category_and_price(item_name)
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    keyboard.row(button(f"{item_name} - {price} руб", "basket"))
    keyboard.add(button("-", f"basket_remove_{item_name}"),
                 button(f"{quantity} шт - {price * quantity} руб", "basket"),
                 button("+", f"basket_add_{item_name}"))
    keyboard.add(button("Удалить из корзины", f"clear_item_in_basket_{item_name}"),
                 button("Назад", "basket"))
    return keyboard


def menu_neiro_burger():
    keyboard = types.InlineKeyboardMarkup()
    for burger in burgers:
        keyboard.row(button(burger[0],burger[0]))
    keyboard.row(button("Корзина","basket"))
    keyboard.row(button("Назад","menu"))
    return keyboard
def menu_neiro_drinks():
    keyboard = types.InlineKeyboardMarkup()
    for drink in drinks:
        keyboard.row(button(drink[0],drink[0]))
    keyboard.row(button("Корзина","basket"))
    keyboard.row(button("Назад","menu"))
    return keyboard
def menu_neiro_combo():
    keyboard = types.InlineKeyboardMarkup()
    for combo in combos:
        keyboard.row(button(combo[0],combo[0]))
    keyboard.row(button("Корзина","basket"))
    keyboard.row(button("Назад","menu"))
    return keyboard
def menu_neiro_deserts():
    keyboard = types.InlineKeyboardMarkup()
    for desert in deserts:
        keyboard.row(button(desert[0],desert[0]))
    keyboard.row(button("Корзина","basket"))
    keyboard.row(button("Назад","menu"))
    return keyboard
def menu_neiro_salads():
    keyboard = types.InlineKeyboardMarkup()
    for salad in salads:
        keyboard.row(button(salad[0],salad[0]))
    keyboard.row(button("Корзина","basket"))
    keyboard.row(button("Назад","menu"))
    return keyboard
def menu_neiro_sous():
    keyboard = types.InlineKeyboardMarkup()
    for souss in sous:
        keyboard.row(button(souss[0],souss[0]))
    keyboard.row(button("Корзина","basket"))
    keyboard.row(button("Назад","menu"))
    return keyboard
def display_basket(user_id, username):
    user_basket = get_user_basket(user_id, username)
    total_cost = 0
    if user_basket:
        basket_text = "*Ваша корзина:*\n\n"
        for item, quantity in user_basket.items():
            category, price, _ = find_category_and_price(item)
            
            # Проверка значений, возвращаемых функцией find_category_and_price
            print(f"Item: {item}, Category: {category}, Price: {price}")
            
            if price is None:
                # Если цена None, выведем сообщение об ошибке
                print(f"Error: Price for item '{item}' is None")
                continue  # Пропускаем этот элемент
            
            item_cost = price * quantity
            total_cost += item_cost
            basket_text += f"*{item}: {item_cost} руб* | ({quantity} шт x {price} руб)\n"
        basket_text += f"\nОбщая стоимость: *{total_cost}* руб"
        basket_text += "\nВы можете добавить или удалить товары."
    else:
        basket_text = "*Ваша корзина пуста.*"
    return basket_text

def basket_button(user_id, username):
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    user_basket = get_user_basket(user_id, username)
    if user_basket:
        for item, quantity in user_basket.items():
            # Заменяем пробелы в названии товара на подчеркивания
            item_safe = item.replace(' ', '_')
            keyboard.row(button(f"{item}", f"item_{item_safe}"))
        keyboard.add(button("Очистить корзину", "clear_basket"), button("Назад", "menu"))
    else:
        keyboard.row(button("Добавить товар в корзину", "menu"))
        keyboard.row(button("Назад", "back"))
    return keyboard


def find_category_and_price(call_data):
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
            media = types.InputMediaPhoto(open(photo_path, "rb"), caption=text, parse_mode="Markdown")
            bot.edit_message_media(media, call.message.chat.id, call.message.id, reply_markup=reply_markup)
            log(call, False, call.data)
@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
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
        item_name = call.data.split('_')[1]
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
        media = types.InputMediaPhoto(open(photo_path, "rb"), caption=text, parse_mode="Markdown")
        bot.edit_message_media(media, call.message.chat.id, call.message.id, reply_markup=basket_button(user_id, username))
        log(call, False, call.data)
    elif call.data.startswith('clear_item_in_basket_'):
        item_name_safe = call.data.split('_', 4)[4]
        # Восстанавливаем пробелы в названии товара
        item_name = item_name_safe.replace('_', ' ')
        clear_item_in_basket(user_id, username, item_name)
        text = f"*Товар {item_name} был удалён из корзины*"
        photo_path = 'img/LogoNeiroFood.jpg'
        print(basket_button(user_id, username))
        print(user_id)
        print(username)
        media = types.InputMediaPhoto(open(photo_path, "rb"), caption=text, parse_mode="Markdown")
        bot.edit_message_media(media, call.message.chat.id, call.message.id, reply_markup=basket_button(user_id, username))
        log(call, False, call.data)

    elif call.data == 'back':
        text = '''Привет! Я ваш личный ассистент NeiroFood!'''
        photo_path = 'img/LogoNeiroFood.jpg'
        media = types.InputMediaPhoto(open(photo_path, "rb"), caption=text, parse_mode="Markdown")
        bot.edit_message_media(media, call.message.chat.id, call.message.id, reply_markup=menu_tool_button())
        log(call, False, call.data)
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
    



if __name__ == '__main__':
    try:
        on_ready()
        bot.polling()
    except Exception as e:
        printt(f"Ошибка при работе бота: {e}")
        logger.info(f"Ошибка при работе бота: {e}")
