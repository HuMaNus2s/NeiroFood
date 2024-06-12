import os
import telebot
from telebot import types
import json
import logging
from logging.handlers import RotatingFileHandler
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
rec_time = now.strftime("%d %B %Y %H:%M")
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
        logger.error(f'{e}')
def on_ready():
    try:
        printt("BOT ACTIVATED!")
        logger.info('BOT ACTIVATED!')
    except Exception as e:
        printt(f"Бот аварийно прекратил работу: {e}")
        logger.critical(f'{e}')
def log(message=None, error=False, button=None, purchase=None):
    try:
        user = message.from_user.username if message.from_user.username else message.from_user.id       
        if not error and not button and not purchase:
            printt(f'{user} использовал команду <{message.text}>')
            logger.info(f'{user} использовал команду <{message.text}>')
        elif not error and button:
            button_parts = button.split("_")
            if len(button_parts) >= 3:
                action = button_parts[1]
                if action == "add":
                    printt(f'{user} добавил в корзину <{button_parts[2]}>')
                    logger.info(f'{user} добавил в корзину <{button_parts[2]}>')
                elif action == "remove":
                    printt(f'{user} удалил из корзины <{button_parts[2]}>')
                    logger.info(f'{user} удалил из корзины <{button_parts[2]}>')
                else:
                    printt(f'{user} использовал кнопку <{button}>')
                    logger.info(f'{user} использовал кнопку <{button}>')
            else:
                printt(f'{user} использовал кнопку <{button}>')
                logger.info(f'{user} использовал кнопку <{button}>')
        elif not error and purchase:
            printt(f'{user} успешно завершил покупку <{purchase}>')
            logger.info(f'{user} успешно завершил покупку <{purchase}>')
        else:
            printt(f'Неизвестная команда <{message.text}>')
            logger.warning(f'Неизвестная команда <{message.text}>')
    except Exception as e:
        printt(f"Ошибка при формировании логов: {e}")
        logger.error(f'Ошибка при формировании логов: {e}')

# Работа с корзинами пользователей

def get_user_basket(user_id, username):
    try:
        if username is None:
            file_path = f'users/{user_id}.json'
        else:
            username = username.replace(" ", "_")
            file_path = f'users/{user_id}_{username}.json'
        if not os.path.exists('users'):
            os.makedirs('users')
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump({}, file, ensure_ascii=False, indent=4)
            printt(f'Новый пользователь: {user_id}_{username}.json')
            logger.info(f'Новый пользователь: {user_id}_{username}.json')
        
        # Чтение содержимого файла
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        printt(f"Ошибка при чтении json файла {user_id}_{username}: {e}")
        logger.error(f'{e}')
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
        logger.error(f'{e}')

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
        logger.error(f'{e}')

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
        logger.error(f'{e}')

burgers = [
    ('Ангус ШЕФ', 339, '*Ангус ШЕФ* — это настоящий гастрономический шедевр. Он состоит из 150 граммов мраморной говядины высочайшего качества, приготовленной на открытом огне. Французская булочка бриошь, свежие овощи, лук фри, хрустящий бекон и ароматный голландский сыр - все это делает этот бургер по-настоящему изысканным и неповторимым. Каждый грызок будет наслаждаться сочным мясом, сочным и нежным вкусом булочки и ароматными добавками.\n\n*Пищевая ценность БЖУ*\nЭнергия   — *3932.96 кДж*\nКалории  — *940 ККал*\nБелки       — *37 г*\nЖиры       — *60 г*\nУглеводы — *64 г*\nВес: *338 г*'),
    ('Двойной ВОППЕР', 289, '*Двойной Воппер* — это два аппетитных, приготовленных на огне бифштекса из 100% говядины с сочными помидорами, свежим нарезанным листовым салатом, густым майонезом, хрустящими маринованными огурчиками и свежим луком на нежной булочке с кунжутом. Двойное удовольствие!\n\n*Пищевая ценность БЖУ*\nЭнергия   — *3891.12 кДж*\nКалории  — *930 ККал*\nБелки       — *37 г*\nЖиры       — *58 г*\nУглеводы — *53 г*\nВес: *312 г*'),
    ('Родео Бургер', 150, '*Родео Бургер* — это незабываемое сочетание вкусов. Говяжий бифштекс, кольца лука в кляре, соус Барбекю и американский сыр на булочке с кунжутом создают неповторимую гармонию вкусов. Этот бургер подойдет для тех, кто любит насыщенные и пикантные вкусы.\n\n*Пищевая ценность БЖУ*\nЭнергия   — *2175.68 кДж*\nКалории  — *520 ККал*\nБелки       — *20 г*\nЖиры       — *26 г*\nУглеводы — *48 г*\nВес: *168 г*'),
    ('Цезарь КИНГ', 150, '*Цезарь КИНГ* — это классика в новом исполнении. Говяжий бифштекс, свежие листья салата, сочные помидоры, тертый пармезан и соус Цезарь на булочке с кунжутом. Этот бургер сочетает в себе свежесть и насыщенность вкусов.\n\n*Пищевая ценность БЖУ*\nЭнергия   — *2886.96 кДж*\nКалории  — *690 ККал*\nБелки       — *26 г*\nЖиры       — *42 г*\nУглеводы — *43 г*\nВес: *295 г*'),
    ('ЦЭНСИ', 150, '*ЦЭНСИ* — это бургер для истинных гурманов. Говяжий бифштекс, бекон, американский сыр, свежие листья салата и помидоры, соус Сендвич на булочке с кунжутом. Он подарит вам насыщенный вкус и оставит приятное послевкусие.\n\n*Пищевая ценность БЖУ*\nЭнергия   — *2426.72 кДж*\nКалории  — *580 ККал*\nБелки       — *24 г*\nЖиры       — *36 г*\nУглеводы — *37 г*\nВес: *201 г*'),
    ('Баварский бургер', 150, '*Баварский бургер* — это идеальное сочетание говяжьего бифштекса, бекона и немецких колбасок, приправленных горчицей и луком на булочке с кунжутом. Этот бургер наполнен насыщенными и пикантными вкусами, которые подарят вам настоящее удовольствие.\n\n*Пищевая ценность БЖУ*\nЭнергия   — *3263.52 кДж*\nКалории  — *780 ККал*\nБелки       — *30 г*\nЖиры       — *44 г*\nУглеводы — *60 г*\nВес: *270 г*'),
    ('Черная МАМБА', 150, '*Черная МАМБА* — это бургер, который выделяется своей уникальностью. Говяжий бифштекс, соус из черного трюфеля, свежие листья салата, помидоры и сыр на черной булочке. Этот бургер удивит вас своими необычными и изысканными вкусами.\n\n*Пищевая ценность БЖУ*\nЭнергия   — *3556.4 кДж*\nКалории  — *850 ККал*\nБелки       — *28 г*\nЖиры       — *50 г*\nУглеводы — *67 г*\nВес: *255 г*'),
    ('Зеленный ФРЕШ', 150, '*Зеленный ФРЕШ* — это бургер для любителей свежих и легких вкусов. Говяжий бифштекс, свежие листья салата, огурцы и йогуртовый соус на булочке с отрубями. Он идеально подойдет для тех, кто ценит здоровую и вкусную еду.\n\n*Пищевая ценность БЖУ*\nЭнергия   — *2343.04 кДж*\nКалории  — *560 ККал*\nБелки       — *22 г*\nЖиры       — *32 г*\nУглеводы — *44 г*\nВес: *230 г*'),
    ('Двойной Чизбургер', 150, '*Двойной Чизбургер* — это два говяжьих бифштекса, два ломтика сыра Чеддер, маринованные огурцы, лук, кетчуп и горчица на булочке с кунжутом. Этот бургер подарит вам насыщенный и сырный вкус, который не оставит вас равнодушным.\n\n*Пищевая ценность БЖУ*\nЭнергия   — *2133.84 кДж*\nКалории  — *510 ККал*\nБелки       — *23 г*\nЖиры       — *29 г*\nУглеводы — *38 г*\nВес: *155 г*'),
]

drinks = [
    ('Coca-Cola', 55, '*Coca-Cola* — освежающий напиток с классическим вкусом, который известен и любим по всему миру. Ледяная Кока-Кола прекрасно утоляет жажду и дарит бодрость.\n\n*Пищевая ценность БЖУ*\nЭнергия   — *176 кДж*\nКалории  — *42 ККал*\nБелки       — *0 г*\nЖиры       — *0 г*\nУглеводы — *11 г*\nВес: *330 мл*'),
    ('Sprite', 55, '*Sprite* — лимонад с легким лимонным вкусом, идеально утоляющий жажду и дарящий свежесть. Этот газированный напиток отлично подойдет для любого времени года.\n\n*Пищевая ценность БЖУ*\nЭнергия   — *176 кДж*\nКалории  — *42 ККал*\nБелки       — *0 г*\nЖиры       — *0 г*\nУглеводы — *11 г*\nВес: *330 мл*'),
    ('Lipton', 55, '*Lipton* — освежающий чай со вкусом лимона. Легкий и ароматный, этот напиток станет отличным дополнением к любому приему пищи.\n\n*Пищевая ценность БЖУ*\nЭнергия   — *168 кДж*\nКалории  — *40 ККал*\nБелки       — *0 г*\nЖиры       — *0 г*\nУглеводы — *10 г*\nВес: *330 мл*'),
    ('КЛУБНИЧНЫЙ ШЕЙК', 55, '*Клубничный шейк* — сладкий молочный коктейль с насыщенным клубничным вкусом. Он освежит вас и подарит настоящее наслаждение.\n\n*Пищевая ценность БЖУ*\nЭнергия   — *1176 кДж*\nКалории  — *280 ККал*\nБелки       — *6 г*\nЖиры       — *6 г*\nУглеводы — *52 г*\nВес: *250 мл*'),
    ('ШОКОЛАДНЫЙ ШЕЙК', 55, '*Шоколадный шейк* — молочный коктейль с насыщенным шоколадным вкусом, который понравится любителям сладкого.\n\n*Пищевая ценность БЖУ*\nЭнергия   — *1134 кДж*\nКалории  — *270 ККал*\nБелки       — *7 г*\nЖиры       — *7 г*\nУглеводы — *45 г*\nВес: *250 мл*'),
    ('ВАНИЛЬНЫЙ ШЕЙК', 55, '*Ванильный шейк* — молочный коктейль с нежным ванильным вкусом, который подарит вам настоящее наслаждение.\n\n*Пищевая ценность БЖУ*\nЭнергия   — *1176 кДж*\nКалории  — *280 ККал*\nБелки       — *6 г*\nЖиры       — *6 г*\nУглеводы — *52 г*\nВес: *250 мл*'),
]

combos = [
    ('Шримп ВОППЕР', 533, '*Шримп ВОППЕР* — комбо с бургером из креветок, картошкой фри и напитком. Идеальный выбор для любителей морепродуктов и разнообразных вкусов.\n\n*Пищевая ценность БЖУ*\nЭнергия   — *2500 кДж*\nКалории  — *598 ККал*\nБелки       — *22 г*\nЖиры       — *32 г*\nУглеводы — *58 г*\nВес: *420 г*'),
    ('Черная МАМБА Комбо', 630, '*Черная МАМБА* — комбо с бургером "Черная МАМБА", картошкой фри и напитком. Насладитесь необычным сочетанием вкусов и ароматов.\n\n*Пищевая ценность БЖУ*\nЭнергия   — *4432 кДж*\nКалории  — *1058 ККал*\nБелки       — *28 г*\nЖиры       — *50 г*\nУглеводы — *67 г*\nВес: *510 г*'),
    ('Двойной ВОППЕР М', 550, '*Двойной ВОППЕР М* — комбо с двойным ВОППЕРом, картошкой фри и напитком. Двойное мясо для двойного удовольствия.\n\n*Пищевая ценность БЖУ*\nЭнергия   — *4512 кДж*\nКалории  — *1080 ККал*\nБелки       — *37 г*\nЖиры       — *58 г*\nУглеводы — *53 г*\nВес: *610 г*'),
    ('Гамбургер Комбо', 355, '*Гамбургер Комбо* — классическое сочетание гамбургера, картошки фри и напитка. Простой и вкусный выбор на каждый день.\n\n*Пищевая ценность БЖУ*\nЭнергия   — *2133.84 кДж*\nКалории  — *510 ККал*\nБелки       — *23 г*\nЖиры       — *29 г*\nУглеводы — *38 г*\nВес: *470 г*'),
    ('Беконайзер Комбо', 400, '*Беконайзер Комбо* — комбо с бургером "Беконайзер", картошкой фри и напитком. Насладитесь хрустящим беконом и сочным мясом.\n\n*Пищевая ценность БЖУ*\nЭнергия   — *3118.72 кДж*\nКалории  — *746 ККал*\nБелки       — *32 г*\nЖиры       — *44 г*\nУглеводы — *58 г*\nВес: *450 г*'),
    ('Чизбургер Комбо', 455, '*Чизбургер Комбо* — комбо с чизбургером, картошкой фри и напитком. Сочный бургер с сыром для настоящих гурманов.\n\n*Пищевая ценность БЖУ*\nЭнергия   — *3135.84 кДж*\nКалории  — *750 ККал*\nБелки       — *23 г*\nЖиры       — *29 г*\nУглеводы — *38 г*\nВес: *460 г*'),
]

deserts = [
    ('Сырники', 149, '*Сырники* — нежные сырники со сметаной и вареньем. Идеальный десерт для завершения трапезы.\n\n*Пищевая ценность БЖУ*\nЭнергия   — *828 кДж*\nКалории  — *198 ККал*\nБелки       — *10 г*\nЖиры       — *10 г*\nУглеводы — *18 г*\nВес: *100 г*'),
    ('Шоколадный Маффин', 159, '*Шоколадный Маффин* — маффин с насыщенным шоколадным вкусом. Прекрасное дополнение к чашке кофе или чая.\n\n*Пищевая ценность БЖУ*\nЭнергия   — *1104 кДж*\nКалории  — *264 ККал*\nБелки       — *4 г*\nЖиры       — *13 г*\nУглеводы — *34 г*\nВес: *80 г*'),
    ('Пирожок с вишней', 89, '*Пирожок с вишней* — сладкий пирожок с начинкой из вишни. Наслаждение для любителей фруктовых десертов.\n\n*Пищевая ценность БЖУ*\nЭнергия   — *980 кДж*\nКалории  — *234 ККал*\nБелки       — *3 г*\nЖиры       — *12 г*\nУглеводы — *29 г*\nВес: *80 г*'),
    ('Карамельное мороженное', 99, '*Карамельное мороженное* — мороженное с карамельным соусом. Сладкий и освежающий десерт.\n\n*Пищевая ценность БЖУ*\nЭнергия   — *828 кДж*\nКалории  — *198 ККал*\nБелки       — *4 г*\nЖиры       — *9 г*\nУглеводы — *25 г*\nВес: *100 г*'),
    ('Клубничное мороженное', 99, '*Клубничное мороженное* — мороженное с клубничным соусом. Вкусный и освежающий десерт с ягодной ноткой.\n\n*Пищевая ценность БЖУ*\nЭнергия   — *828 кДж*\nКалории  — *198 ККал*\nБелки       — *4 г*\nЖиры       — *9 г*\nУглеводы — *25 г*\nВес: *100 г*'),
    ('Пончики с кремом', 199, '*Пончики с кремом* — пончики с нежным кремом. Прекрасный выбор для сладкоежек.\n\n*Пищевая ценность БЖУ*\nЭнергия   — *1255 кДж*\nКалории  — *300 ККал*\nБелки       — *4 г*\nЖиры       — *16 г*\nУглеводы — *37 г*\nВес: *80 г*'),
]

salads = [
    ('Страчателла', 255, '*Страчателла* — салат с сыром страчателла и свежими овощами. Легкий и освежающий, идеально подойдет для летнего обеда.\n\n*Пищевая ценность БЖУ*\nЭнергия   — *1204 кДж*\nКалории  — *288 ККал*\nБелки       — *10 г*\nЖиры       — *24 г*\nУглеводы — *10 г*\nВес: *250 г*'),
    ('Салат греческий', 455, '*Салат греческий* — классический греческий салат с фетой и оливками. Свежий и полезный, он станет отличным дополнением к основному блюду.\n\n*Пищевая ценность БЖУ*\nЭнергия   — *837.6 кДж*\nКалории  — *200 ККал*\nБелки       — *5 г*\nЖиры       — *18 г*\nУглеводы — *10 г*\nВес: *300 г*'),
    ('Салат Цезарь', 360, '*Салат Цезарь* — салат "Цезарь" с курицей, пармезаном и соусом цезарь. Сочетание вкусов и текстур, которое не оставит равнодушным.\n\n*Пищевая ценность БЖУ*\nЭнергия   — *1674 кДж*\nКалории  — *400 ККал*\nБелки       — *30 г*\nЖиры       — *24 г*\nУглеводы — *12 г*\nВес: *250 г*'),
]

sous = [
    ('Кетчуп', 55, '*Кетчуп* — Идеально подходит для различных блюд.\n\n*Пищевая ценность БЖУ*\nЭнергия   — *276 кДж*\nКалории  — *66 ККал*\nБелки       — *1 г*\nЖиры       — *0 г*\nУглеводы — *15 г*\nВес: *100 г*'),
    ('Сырный соус', 55, '*Сырный* — Насыщенный и ароматный, он добавит вашим блюдам новый вкус.\n\n*Пищевая ценность БЖУ*\nЭнергия   — *1008 кДж*\nКалории  — *240 ККал*\nБелки       — *3 г*\nЖиры       — *24 г*\nУглеводы — *6 г*\nВес: *100 г*'),
    ('Кисло-сладкий соус', 55, '*Кисло-сладкий* — Идеально подходит для мясных и овощных блюд.\n\n*Пищевая ценность БЖУ*\nЭнергия   — *464 кДж*\nКалории  — *111 ККал*\nБелки       — *0 г*\nЖиры       — *0 г*\nУглеводы — *27 г*\nВес: *100 г*'),
    ('Чесночный соус', 55, '*Чесночный* — соус с насыщенным чесночным вкусом. Прекрасное дополнение к мясу и рыбе.\n\n*Пищевая ценность БЖУ*\nЭнергия   — *1008 кДж*\nКалории  — *240 ККал*\nБелки       — *1 г*\nЖиры       — *24 г*\nУглеводы — *6 г*\nВес: *100 г*'),
    ('Горчичный', 55, '*Горчичный* — Острый и ароматный, идеально подходит для различных блюд.\n\n*Пищевая ценность БЖУ*\nЭнергия   — *672 кДж*\nКалории  — *160 ККал*\nБелки       — *0 г*\nЖиры       — *16 г*\nУглеводы — *8 г*\nВес: *100 г*'),
    ('Барбекю', 55, '*Барбекю* — Идеально подходит для мясных блюд и гриля.\n\n*Пищевая ценность БЖУ*\nЭнергия   — *424 кДж*\nКалории  — *101 ККал*\nБелки       — *1 г*\nЖиры       — *0 г*\nУглеводы — *24 г*\nВес: *100 г*'),
]

def button(name, callback):
    try:
        return types.InlineKeyboardButton(name, callback_data=callback)
    except Exception as e:
        printt(f"Ошибка при создании кнопки {name} ведущую в {callback}: {e}")
        logger.error(f'{e}')

def back_button(call):
    try:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.row(button("Назад",call))
        return keyboard
    except Exception as e:
        printt(f"Ошибка возвращении в {call}: {e}")
        logger.error(f'{e}')
def menu_tool_button():
    try:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.row(button("О нас", "about"), button("FAQ", "FAQ"))
        keyboard.row(button("Меню", "menu"), button("Корзина", "basket"))
        return keyboard
    except Exception as e:
        printt(f"Неудалось создать кнопки главного меню: {e}")
        logger.error(f'{e}')
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
        logger.error(f'{e}')

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
        keyboard.row(button("Ещё товары", "menu"), button("Оформить покупку", f"buy_{item_name}"), button("Корзина", "basket"))
        keyboard.add(button("Удалить из корзины", f"clear_item_in_basket_{item_name}"), button("Назад", "basket")) 
        return keyboard
    except Exception as e:
        printt(f"Ошибка при создании позиции товара: {e}")
        logger.error(f'{e}')

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
        logger.error(f'{e}')
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
        logger.error(f'{e}')
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
        logger.error(f'{e}')
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
        logger.error(f'{e}')
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
        logger.error(f'{e}')
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
        logger.error(f'{e}')

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
        logger.error(f'{e}')

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
        logger.error(f'{e}')


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
        logger.error(f'{e}')

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
        logger.error(f'{e}')
@bot.message_handler(commands=['help'])
def handle_help(message):
    try:
        bot.reply_to(message, f"Список доступных команд:\n\n{command_name(0)} - приветствие\n{command_name(1)} - справка")
        log(message=message)
    except Exception as e:
        printt(f"Ошибка при использовании команды help: {e}")
        logger.error(f'{e}')
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
                log(message=call, error=False, button=call.data)
    except Exception as e:
        printt(f"Ошибка вызова {call}: {e}")
        logger.error(f'{e}')
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
            log(message=call, error=False, button=call.data)
        elif call.data.startswith('item_'):
            item_name = call.data.split('_',1)[1].replace("_"," ")
            quantity = get_user_basket(user_id, username).get(item_name, 0)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=button_for_basket(item_name, quantity))
            log(message=call, error=False, button=call.data)

        elif call.data == 'basket':
            text = display_basket(user_id, username)
            photo_path = 'img/LogoNeiroFood.jpg'
            media = types.InputMediaPhoto(open(photo_path, "rb"), caption=text, parse_mode="Markdown")
            bot.edit_message_media(media, call.message.chat.id, call.message.id, reply_markup=basket_button(user_id, username))
            log(message=call, error=False, button=call.data)

        elif call.data == 'clear_basket':
            clear_user_basket(user_id, username)
            text = "*Ваша корзина была очищена.*"
            photo_path = 'img/LogoNeiroFood.jpg'
            print(basket_button(user_id, username))
            media = types.InputMediaPhoto(open(photo_path, "rb"), caption=text, parse_mode="Markdown")
            bot.edit_message_media(media, call.message.chat.id, call.message.id, reply_markup=basket_button(user_id, username))
            log(message=call, error=False, button=call.data)
        elif call.data.startswith('clear_item_in_basket_'):
            item_name = call.data.split('_', 4)[4].replace('_', ' ')
            clear_item_in_basket(user_id, username, item_name)
            text = f"*Товар {item_name} был удалён из корзины*"
            photo_path = 'img/LogoNeiroFood.jpg'
            print(basket_button(user_id, username))
            media = types.InputMediaPhoto(open(photo_path, "rb"), caption=text, parse_mode="Markdown")
            bot.edit_message_media(media, call.message.chat.id, call.message.id, reply_markup=basket_button(user_id, username))
            log(message=call, error=False, button=call.data)

        elif call.data == 'back':
            text = '''Привет! Я ваш личный ассистент NeiroFood!'''
            photo_path = 'img/LogoNeiroFood.jpg'
            media = types.InputMediaPhoto(open(photo_path, "rb"), caption=text, parse_mode="Markdown")
            bot.edit_message_media(media, call.message.chat.id, call.message.id, reply_markup=menu_tool_button())
            log(message=call, error=False, button=call.data)
            
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
            log(message=call, error=False, button=call.data)
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
                    description=f"Номер заказа: {str(random.randint(0, 9999)).zfill(4)} | {rec_time}",
                    provider_token=config['payments_token'],
                    currency="RUB",
                    prices=[labeled_price],
                    start_parameter="time-machine-example",
                    invoice_payload=f"item_purchase_{item_name}"
                )
                bot.delete_message(call.message.chat.id, call.message.message_id)
            else:
                bot.answer_callback_query(call.id, "Товар не найден в корзине.")
            log(message=call, error=False, button=call.data)
            return

        if category:
            photo_path = f'img/{category}/{call.data}.png'
            try:
                media = types.InputMediaPhoto(open(photo_path, "rb"), caption=f"*{call.data}* — *{price} руб*\n{description}", parse_mode="Markdown")
                quantity = get_user_basket(user_id, username).get(call.data, 0)
                bot.edit_message_media(media, call.message.chat.id, call.message.id, reply_markup=button_for_basket(call.data, quantity))
                log(message=call, error=False, button=call.data)
            except Exception as e:
                print(f"Ошибка при открытии файла: {e}")
                logger.error(f'{e}')
        else:
            pass  
    except Exception as e:
        printt(f"Ошибка: {e}")
        logger.error(f'{e}')
# Обработчик успешной оплаты
@bot.pre_checkout_query_handler(func=lambda query: True)
def process_pre_checkout_query(pre_checkout_query):
    try:
        bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
    except Exception as e:
        printt(f"Ошибка при обработке оплаты: {e}")
        logger.error(f'{e}')

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
        
        log(message=message, purchase=payload)
    except Exception as e:
        printt(f"Ошибка при постобработке заказа: {e}")
        logger.error(f'{e}')
    
if __name__ == '__main__':
    try:
        on_ready()
        bot.polling()
    except Exception as e:
        printt(f"Ошибка при работе бота: {e}")
        logger.error(f"Ошибка при работе бота: {e}")
