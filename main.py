import re
import random
import telebot
import wikipedia
import sqlite3
from pyexpat.errors import messages
from telebot.apihelper import set_message_reaction
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

import save
from telebot import types

bot = telebot.TeleBot(save.token)
connect =  sqlite3.connect("users.db", check_same_thread=False)
cursor = connect.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users(id INT)")
connect.commit()

num = False
game = False
admins = [2134765278]
text = ""
link = ""
send = ""
client = []
@bot.message_handler(commands=['start'])
def info(message):
    if message.chat.id in admins:
        help(message)
    else:
        client.append(message.chat.id)
        help_user(message)
        try:
            id = message.chat.id
            result_bd = cursor.execute("SELECT * FROM users WHERE id=?",(id,)).fetchone()
            if not result_bd:
                cursor.execute("INSERT INTO users (id) VALUES (?)", (id,))
                connect.commit()
                bot.send_message(message.chat.id, "TI PODPISALSA")
            else:
                bot.send_message(message.chat.id, "ERROR")

        except:
            bot.send_message(message.chat.id,"WARNING")
        print( client)
def help_user(message):
    reply_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    reply_markup.add(types.KeyboardButton("Википедия"))
    reply_markup.add(types.KeyboardButton("Угадайка"))
    bot.send_message(message.chat.id, "Выбери что показать", reply_markup=reply_markup)

    # print(message.chat.id)
    # markup_inline = types.InlineKeyboardMarkup()
    # markup_inline.add(
    #     types.InlineKeyboardButton(text="да", callback_data="yes"),
    #     types.InlineKeyboardButton(text="нет", callback_data="no")
    # )
    # bot.send_message(message.chat.id, "Поиграй со мной", reply_markup=markup_inline)
def help(message):
    bot.send_message(message.chat.id,"Команды бота:\n"
                    "/edit_message - редактирование сообщений\n"
                    "/edit_link - редактирование ссылки\n"
                    "/show_message - показать сообщение\n"
                    "/send_message или send - отправить сообщение\n"
                    "/help - помощь")

@bot.message_handler(commands=['edit_message'])
def edit_message(message):
    if message.chat.id in admins:
        m = bot.send_message(message.chat.id, "введи текст")
        bot.register_next_step_handler(m, add_message)
def add_message(message):
    global text
    text = message.text
    if text not in ["изменить ссылку"]:
        bot.send_message(message.chat.id,f" Сохр.текссе:{text}")
    else:
        bot.send_message(message.chat.id, "некоректно")



@bot.message_handler(commands=['edit_link'])
def edit_message(message):
    if message.chat.id in admins:
        m = bot.send_message(message.chat.id, "ссылкку")
        bot.register_next_step_handler(m, add_link)
def add_link(message):
    global link
    link = message.text
    regex = re.compile(
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # проверка dot
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # проверка ip 
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    if link is not None and regex.search(link):

        if link not in ["изменить ссылку"]:
            bot.send_message(message.chat.id,f" Сохр.ссылка:{link}")
        else:
            bot.send_message(message.chat.id, "некоректно")
@bot.message_handler(commands=['send', 'send_message'])
def send(message):
    global  text,link
    if message.chat.id in admins:
       if text != "":
           if link != "":
               cursor.execute("SELECT id FROM users ")
               massive = cursor.fetchall()
               for i in massive:
                   id = i[0]
                   sending(id)
               else:
                   text = ""
                   link = ""
               pass
def sending(i):
    markup = types.InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text="перейти по ссылке", url=link))
    bot.send_message(i,text, reply_markup=markup)




def process_broadcast(message):
    if not message.text.strip():
        bot.reply_to(message, "может быть пустым")
        pass

    bot.send_message(message.chat.id, f"Сообщение для рассылки: {message.text}")






@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    global num, game
    user_id = call.message.chat.id
    print(call.data)
    if call.data == "yes":
        bot.send_message(user_id, "Ты ответил 'да'")
        reply_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        reply_markup.add(
            types.KeyboardButton("Википедия"),
            types.KeyboardButton("Угадайка")
        )
        bot.send_message(user_id, "Выбери что показать", reply_markup=reply_markup)
    elif call.data == "no":
        bot.send_message(user_id, "Ты ответил 'нет'. Если хочешь, можешь начать снова.")
    elif call.data == str(num) and game:
        bot.send_message(user_id, "Число угадал!.")
        game = False
    elif str(num) != call.data and call.data in ["1","2","3","4","5"] and game:
        game = False
        bot.send_message(user_id, "Число  no угадал!.")
    # else:
    #     bot.send_message(user_id, "Неизвестная команда.")

@bot.message_handler(content_types=["text"])
def mess(message):
    global game
    user_id = message.chat.id
    text = message.text

    if text == 'wiki':
        bot.send_message(user_id, get_wiki(text))
    elif text == "Википедия":
        bot.send_message(user_id, "Напиши что найти?")
    elif text == "Угадайка":
        game = True
        random_num(user_id)
        clawisha(user_id)

wikipedia.set_lang('ru')

def get_wiki(word):
    try:
        w = wikipedia.page(word)
        wikitext = w.content[:1000]
        wikiresult = '. '.join([sentence for sentence in wikitext.split('.') if '==' not in sentence]) + '.'
        wikiresult = re.sub(r'\([^()]*\)', "", wikiresult)
        wikiresult = re.sub(r'\{[^\{\}]*\}', "", wikiresult)
        return wikiresult
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Найдено несколько вариантов: {e.options}"
    except Exception:
        return "Такой статьи нет."

def clawisha(user_id):

    markup_inline = types.InlineKeyboardMarkup()
    markup_inline.add(*[types.InlineKeyboardButton(text=str(i), callback_data=str(i)) for i in range(1, 6)])
    bot.send_message(user_id, "Я загадал число, угадай", reply_markup=markup_inline)

def random_num(user_id):
    global num
    num = random.randint(1, 5)  # Сохраняем загаданное число
    bot.send_message(user_id, "Я загадал число от 1 до 5. Угадай!")



bot.infinity_polling()