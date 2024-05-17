import telebot
from telebot import types


file_for_config = open('config.json', 'r')
config = json.load(file_for_config)
prefix = config['prefix']
# Замените 'YOUR_TOKEN' на токен вашего бота
bot = telebot.TeleBot(config['token'])

# Обработчик команды '/start'
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton("Кнопка 1", callback_data='button1')
    markup.add(button)
    bot.send_message(message.chat.id, "Нажмите на кнопку:", reply_markup=markup)

# Обработчик нажатия на кнопку
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "button1":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Вы нажали на кнопку 1")
        markup = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton("Кнопка 2", callback_data='button2')
        markup.add(button)
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
    elif call.data == "button2":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Вы нажали на кнопку 2")
        markup = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton("Кнопка 3", callback_data='button3')
        markup.add(button)
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
    elif call.data == "button3":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Вы нажали на кнопку 3")

# Запускаем бота
bot.polling()
