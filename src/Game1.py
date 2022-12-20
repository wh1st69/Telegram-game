import telebot
from telebot import types
import json
import time


def get_api_token(filename = 'src/config.json', key = 'token'):
    return json.load(open(filename))[key]

bot = telebot.TeleBot(get_api_token())

commands = ['/start', '/about']

# Function for get the GAMEMAP (Array of vertexes)
def get_map(filename = 'src/GAMEMAP.json'):
    return json.load(open(filename))


# Function for GET current position on the GAMEMAP (it gets value of "pos.json")
def get_pos(user_id):
    return json.load(open('src/pos.json'))[user_id]


# Function for CHANGE current position on the GAMEMAP according to response from user (it resets position after the ending)
def change_pos(user_id, message, filename = 'src/pos.json'):
    with open (filename, 'rt') as _file:
        pos_array = json.load(_file)
    pos_array[user_id] = get_map()[get_pos(user_id)][0][message.text]
    with open (filename, 'wt') as _file:
        json.dump(pos_array, _file, indent=2)

# Function for add new user in database of positions
def add_user_pos(user_id, filename = 'src/pos.json', encoding = 'utf-8'):
    with open (filename, 'rt') as pos:
        user_pos = json.load(pos)
    user_pos[user_id] = 0
    with open(filename, 'wt') as pos:
        json.dump(user_pos, pos, indent=2)

def remove_user_pos(user_id, filename = 'src/pos.json', encoding = 'utf-8'):
    with open(filename, 'rt') as _file:
        user_pos = json.load(_file)
    user_pos.pop(user_id)
    with open(filename, 'wt') as _file:
        json.dump(user_pos, _file, indent=2)


# Function for processing the endings
def endings(user_id, message):
    rmk = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    rmk.add(types.KeyboardButton('/start'))
    bot.send_message(message.chat.id, get_map()[24][0][message.text], reply_markup = rmk)



@bot.message_handler(commands = ['about'])
def about(message, smth = False):
    about_text = f'Игра представляет собой текстовый квест.\nПосле сообщения от бота вам необходимо нажать клавишу, соответствующую вашему выбору.\n\nВ случае, если текст ответов не помещается на кнопках, попробуйте использовать горизонтальную ориентацию Вашего мобильного устройства.\n\nВ любой момент по команде /start вы можете начать заново.\n\nПриятного прохождения!'
    if smth:
        return about_text
    else:
        bot.send_message(message.chat.id, about_text)
        

@bot.message_handler(commands = ['start'])
def start_response(message):
    user_id = str(message.chat.id)
    add_user_pos(user_id)
    rmk = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for x in get_map()[get_pos(user_id)][0]:
        rmk.add(types.KeyboardButton(x))
    text = get_map()[get_pos(user_id)][1]["text"]
    msg = bot.send_photo(message.chat.id, photo = open(get_map()[get_pos(user_id)][1]['photo'], 'rb'), caption = text, reply_markup = rmk)
    bot.register_next_step_handler(msg, response)


def response(message):
    user_id = str(message.chat.id)
    try:
        change_pos(user_id, message)
    except KeyError:
        rmk = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for x in get_map()[get_pos(user_id)][0]:
            rmk.add(types.KeyboardButton(x))
        if message.text == commands[0]:
            start_response(message)
            return
        elif message.text == commands[1]:
            msg = bot.send_message(message.chat.id, about(message, True), reply_markup = rmk)
            bot.register_next_step_handler(msg, response)      
            return              
        else:
            msg = bot.send_message(message.chat.id, 'Не надо писать ничего, на кнопку нажми!', reply_markup = rmk)
            bot.register_next_step_handler(msg, response)
            return
    if get_pos(user_id) == 24:
        remove_user_pos(user_id)
        endings(user_id, message)
        return
    rmk = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for x in get_map()[get_pos(user_id)][0]:
        rmk.add(types.KeyboardButton(x))
    text = get_map()[get_pos(user_id)][1]["text"]
    if 'minigame' in get_map()[get_pos(user_id)][1]:
        bot.send_message(message.chat.id, get_map()[get_pos(user_id) - 1][2][message.text])
        time.sleep(1)
        msg = bot.send_message(message.chat.id, text, reply_markup = rmk)
    elif "photo" in get_map()[get_pos(user_id)][1]:
        msg = bot.send_photo(message.chat.id, photo = open(get_map()[get_pos(user_id)][1]['photo'], 'rb'), caption = text, reply_markup = rmk)
    elif "audio" in get_map()[get_pos(user_id)][1]:
        if "text2" in get_map()[get_pos(user_id)][1]:
            bot.send_message(message.chat.id, text)
            bot.send_audio(message.chat.id, audio = open(get_map()[get_pos(user_id)][1]['audio'], 'rb'))
            time.sleep(9)
            msg = bot.send_message(message.chat.id, get_map()[get_pos(user_id)][1]['text2'], reply_markup = rmk)
        else:
            bot.send_message(message.chat.id, text)
            msg = bot.send_audio(message.chat.id, audio = open(get_map()[get_pos(user_id)][1]['audio'], 'rb'), reply_markup = rmk)
    else:
        msg = bot.send_message(message.chat.id, text, reply_markup = rmk)
    bot.register_next_step_handler(msg, response)
       
        
if __name__ == '__main__':
    bot.polling(none_stop = True)
