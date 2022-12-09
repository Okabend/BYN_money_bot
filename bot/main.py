import telebot
import requests
from telebot import types, TeleBot
from datetime import datetime, time
from apscheduler.schedulers.background import BackgroundScheduler
import time
import logging
import statistics

logging.basicConfig(filename='all_logs.log', encoding='utf-8', level=logging.DEBUG)
logging.debug('This message should go to the log file')
logging.info('So should this')
logging.warning('And this, too')
logging.error('And non-ASCII stuff, too, like Øresund and Malmö')

token = open("token.txt", "r").read()
bot = TeleBot(token)
sched = BackgroundScheduler()
value1 = {}
value2 = {}
str1 = "usd1eur1rub1byn1"
str2 = "usd2eur2rub2byn2"


def today():
    now = datetime.today()
    e_now = now.year
    m_now = now.month
    d_now = now.day
    wd_now = now.weekday
    return e_now, m_now, d_now, wd_now


def val(value):
    e_now, m_now, d_now, wd_now = today()
    num = requests.get(f"https://www.nbrb.by/api/exrates/rates/{value}?parammode=2&ondate="
                       f"{e_now}-{m_now}-{d_now}").json()["Cur_OfficialRate"]
    return num


def distribution():
    e_now, m_now, d_now, wd_now = today()

    with open("subs.txt", "r") as subs:
        for sub in list(subs):
            if wd_now in range(3):
                print("будние дни")
                try:
                    bot.send_message(sub, "Вот такие сегодня курсы валют 🤠")
                    # использую эту конструкцию второй раз, повод создать функцию
                    usd = val("USD")
                    eur = val("EUR")
                    rub = val("RUB")
                    print(usd, eur, rub)
                    bot.send_message(sub, f"🇺🇸 <b>1 USD = {float('{:.3f}'.format(usd))} р</b>\n"
                                                f"🇪🇺 <b>1 EUR = {float('{:.3f}'.format(eur))} р</b>\n"
                                                f"🇷🇺 <b>100 RUB = {float('{:.3f}'.format(rub))} р</b>",
                                           parse_mode="html")
                except Exception as ex:
                    print(ex)
                    bot.send_message(sub, "Что-то пошло не так и вы не смогли получить ежедневную рассылку 🤕",
                                           parse_mode="html")
            if wd_now == 4:
                    print("It's friday today")
                    statistics.main()
                    diagram = open(f"friday_apply/{e_now}-{m_now}-{d_now}.png", "rb")
                    bot.send_photo(sub, diagram)
            else:
                print("not friday")


@bot.message_handler(content_types=["photo"])
def get_user_photo(message):
    "if user send some photo"
    bot.send_message(message.chat.id, "Nice pic bro", parse_mode="html")


@bot.message_handler(commands=["start"])
def options(message):
    "главное меню"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    course = types.KeyboardButton("Курс на сегодня")
    conv = types.KeyboardButton("Конвертер")
    subscribe = types.KeyboardButton("Подписаться на рассылку")
    markup.add(course, conv, subscribe)
    bot.send_message(message.chat.id, "Привет! Выберите нужную опцию:", reply_markup=markup)


@bot.message_handler(content_types=['text'])
def func(message):
    global subs
    id = message.from_user.id
    # this func analise all messages
    if message.text == "Курс на сегодня":
        try:
            usd = val("USD")
            eur = val("EUR")
            rub = val("RUB")
            print(usd, eur, rub)
            bot.send_message(id, f"🇺🇸 <b>1 USD = {float('{:.3f}'.format(usd))} р</b>\n"
                                                         f"🇪🇺 <b>1 EUR = {float('{:.3f}'.format(eur))} р</b>\n"
                                                         f"🇷🇺 <b>100 RUB = {float('{:.3f}'.format(rub))} р</b>",
                                   parse_mode="html")
        except Exception as ex:
            print(ex)
            bot.send_message(id, "Что-то пошло не так", parse_mode="html")
    if message.text == "Конвертер":
        keyboard = types.InlineKeyboardMarkup()
        usd_button = types.InlineKeyboardButton("🇺🇸 USD", callback_data="usd1")
        eur_button = types.InlineKeyboardButton("🇪🇺 EUR", callback_data="eur1")
        rub_button = types.InlineKeyboardButton("🇷🇺 RUB", callback_data="rub1")
        byn_button = types.InlineKeyboardButton("🇧🇾 BYN", callback_data="byn1")
        keyboard.row(usd_button, eur_button, rub_button, byn_button)
        bot.send_message(id, "Выберите первую валюту", reply_markup=keyboard)
    if message.text == "Подписаться на рассылку":
        with open("subs.txt", "r") as s:
            if f"{id}\n" not in list(s):
                with open("subs.txt", "a") as s:
                    s.write(str(id) + "\n")
                print(f"{id} подписался")
                bot.send_message(id,
                                       "Вы успешно подписались на рассылку. Отменить её можно в любой момент.\n"
                                       "Каждый будний день вы будете получать актуальные курсы основных валют,"
                                       " а в пятницу недельный график")
            else:
                keyboard = types.InlineKeyboardMarkup()
                unsubscribe = types.InlineKeyboardButton("Отписаться", callback_data="unsub")
                keyboard.row(unsubscribe)
                bot.send_message(id, "Вы уже подписаны на рассылку. Желаете отписаться от неё?",
                                       reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == "unsub")
def unsub(callback_obj: telebot.types.CallbackQuery):
    with open("subs.txt", "r") as subs:
        list_subs = list(subs)
        with open("subs.txt", "w") as subs:
            if f"{callback_obj.from_user.id}\n" in list_subs:
                list_subs.remove(f"{callback_obj.from_user.id}\n")
                print(f"{callback_obj.from_user.id} отписался")
                subs.writelines(list_subs)
                bot.send_message(callback_obj.from_user.id, "Вы успешно отписались от рассылки")
            else:
                bot.send_message(callback_obj.from_user.id, "Вы не можете отписаться от рассылки, так как на неё не подписаны")
                subs.writelines(list_subs)
    print(list_subs)


@bot.callback_query_handler(func=lambda call: call.data in str1)
def unsub(callback_obj: telebot.types.CallbackQuery):
    keyboard = types.InlineKeyboardMarkup()
    usd_button = types.InlineKeyboardButton("🇺🇸 USD", callback_data="usd2")
    eur_button = types.InlineKeyboardButton("🇪🇺 EUR", callback_data="eur2")
    rub_button = types.InlineKeyboardButton("🇷🇺 RUB", callback_data="rub2")
    byn_button = types.InlineKeyboardButton("🇧🇾 BYN", callback_data="byn2")
    keyboard.row(usd_button, eur_button, rub_button, byn_button)

    # сделать словарь вместо ифов {["usd1", "usd2"]:"🇺🇸"}

    if callback_obj.data == "usd1":
         bot.send_message(callback_obj.from_user.id, "Вы выбрали 🇺🇸")
    if callback_obj.data == "eur1":
         bot.send_message(callback_obj.from_user.id, "Вы выбрали 🇪🇺")
    if callback_obj.data == "rub1":
         bot.send_message(callback_obj.from_user.id, "Вы выбрали 🇷🇺")
    if callback_obj.data == "byn1":
         bot.send_message(callback_obj.from_user.id, "Вы выбрали 🇧🇾")
    bot.send_message(callback_obj.from_user.id, "Выберите вторую валюту", reply_markup=keyboard)
    global value1
    value1[callback_obj.from_user.id] = callback_obj.data
    print(value1)

    bot.answer_callback_query(callback_query_id=callback_obj.id)


@bot.callback_query_handler(func=lambda call: call.data in str2)
def calculate(callback_obj: telebot.types.CallbackQuery):
    if callback_obj.data == "usd2":
         bot.send_message(callback_obj.from_user.id, "Вы выбрали 🇺🇸")
    if callback_obj.data == "eur2":
         bot.send_message(callback_obj.from_user.id, "Вы выбрали 🇪🇺")
    if callback_obj.data == "rub2":
         bot.send_message(callback_obj.from_user.id, "Вы выбрали 🇷🇺")
    if callback_obj.data == "byn2":
         bot.send_message(callback_obj.from_user.id, "Вы выбрали 🇧🇾")
    global value2
    value2[callback_obj.from_user.id] = callback_obj.data
    print(value2)
    msg = bot.send_message(callback_obj.from_user.id, "введите сумму")
    bot.register_next_step_handler(msg, get_sum)

    bot.answer_callback_query(callback_query_id=callback_obj.id)


def get_sum(message):
    text = message.text
    text_er = text[:]
    v1 = value1[message.from_user.id]
    v2 = value2[message.from_user.id]
    print(v1 + v2)
    if (text.replace(".", "", 1).isdigit() or text.replace(",", "", 1).isdigit()) and len(v1) > 3 and len(v2) > 3:
        text = float(text)
        if v1[:-1] == "usd":
            text = text * ( val("USD"))
        elif v1[:-1] == "rub":
            text = text * ( val("RUB") / 100)
        elif v1[:-1] == "eur":
            text = text * ( val("EUR"))

        if v2[:-1] == "usd":
            text = text / ( val("USD"))
        elif v2[:-1] == "rub":
            text = text / ( val("RUB") / 100)
        elif v2[:-1] == "eur":
            text = text / ( val("EUR"))
        bot.send_message(message.from_user.id,
                               f"{text_er} {v1.upper()[:-1]} = {float('{:.3f}'.format(text))} {v2.upper()[:-1]}")
    elif len(v1) < 4:
        bot.send_message(message.from_user.id, "Вы не выбрали первую валюту")
    else:
        bot.send_message(message.from_user.id, "Вы ввели не число\n\nПопробуйте ещё раз")


if __name__ == "__main__":
    bot.polling(none_stop=True)
    sched.add_job(distribution, 'cron', hour=12,)
    sched.start()