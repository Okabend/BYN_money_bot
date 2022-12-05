import telebot
import requests
import asyncio
from telebot import types
from telebot.async_telebot import AsyncTeleBot
from datetime import datetime, time
import aioschedule as schedule
import time
import statistics

token = open("token.txt", "r").read()
bot = AsyncTeleBot(token)

value1 = {}
value2 = {}
str1 = "usd1eur1rub1byn1"
str2 = "usd2eur2rub2byn2"
subs = []
with open("subs.txt", "r") as f:
    for line in f:
        subs.append(line)

print("считал из файла")
print(subs)


async def today():
    now = datetime.today()
    e_now = now.year
    m_now = now.month
    d_now = now.day
    wd_now = now.weekday
    return e_now, m_now, d_now, wd_now


async def val(value):
    e_now, m_now, d_now, wd_now = await today()
    num = requests.get(f"https://www.nbrb.by/api/exrates/rates/{value}?parammode=2&ondate="
                       f"{e_now}-{m_now}-{d_now}").json()["Cur_OfficialRate"]
    return num


async def distribution():
    e_now, m_now, d_now, wd_now = await today()
    await asyncio.sleep(1)
    with open("subs.txt", "r") as f:
        for line in f:
            subs.append(line)
    for sub in subs:
        print("будние дни")
        try:
            await bot.send_message(sub, "Вот такие сегодня курсы валют 🤠")
            # использую эту конструкцию второй раз, повод создать функцию
            usd = await val("USD")
            eur = await val("EUR")
            rub = await val("RUB")
            print(usd, eur, rub)
            await bot.send_message(sub, f"🇺🇸 <b>1 USD = {float('{:.3f}'.format(usd))} р</b>\n"
                                        f"🇪🇺 <b>1 EUR = {float('{:.3f}'.format(eur))} р</b>\n"
                                        f"🇷🇺 <b>100 RUB = {float('{:.3f}'.format(rub))} р</b>",
                                   parse_mode="html")
        except Exception as ex:
            print(ex)
            await bot.send_message(sub, "Что-то пошло не так и вы не смогли получить ежедневную рассылку 🤕",
                                   parse_mode="html")
        if str(wd_now) == "4":
            print("It's friday today")
            statistics.main()
            diagram = open(f"friday_apply/{e_now}-{m_now}-{d_now}.png", "rb")
            await bot.send_photo(sub, diagram)
        else:
            print("not friday")
    else:
        print("не будние")


@bot.message_handler(content_types=["photo"])
async def get_user_photo(message):
    "if user send some photo"
    await bot.send_message(message.chat.id, "Nice pic bro", parse_mode="html")


@bot.message_handler(commands=["start"])
async def options(message):
    "главное меню"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    course = types.KeyboardButton("Курс на сегодня")
    conv = types.KeyboardButton("Конвертер")
    subscribe = types.KeyboardButton("Подписаться на рассылку")
    markup.add(course, conv, subscribe)
    await bot.send_message(message.chat.id, "Привет! Выберите нужную опцию:", reply_markup=markup)


@bot.message_handler(content_types=['text'])
async def func(message):
    global subs
    # this func analise all messages
    if message.text == "Курс на сегодня":
        try:
            usd = await val("USD")
            eur = await val("EUR")
            rub = await val("RUB")
            print(usd, eur, rub)
            await bot.send_message(message.from_user.id, f"🇺🇸 <b>1 USD = {float('{:.3f}'.format(usd))} р</b>\n"
                                                         f"🇪🇺 <b>1 EUR = {float('{:.3f}'.format(eur))} р</b>\n"
                                                         f"🇷🇺 <b>100 RUB = {float('{:.3f}'.format(rub))} р</b>",
                                   parse_mode="html")
        except Exception as ex:
            print(ex)
            await bot.send_message(message.from_user.id, "Что-то пошло не так", parse_mode="html")
    if (message.text == "Конвертер"):
        keyboard = types.InlineKeyboardMarkup()
        usd_button = types.InlineKeyboardButton("🇺🇸 USD", callback_data="usd1")
        eur_button = types.InlineKeyboardButton("🇪🇺 EUR", callback_data="eur1")
        rub_button = types.InlineKeyboardButton("🇷🇺 RUB", callback_data="rub1")
        byn_button = types.InlineKeyboardButton("🇧🇾 BYN", callback_data="byn1")
        keyboard.row(usd_button, eur_button, rub_button, byn_button)
        await bot.send_message(message.from_user.id, "Выберите первую валюту", reply_markup=keyboard)
    if (message.text == "Подписаться на рассылку"):
        if f"{message.from_user.id}\n" not in subs:
            subs.append(f"{message.from_user.id}\n")
            print(subs)
            print("подписался")
            await bot.send_message(message.from_user.id,
                                   "Вы успешно подписались на рассылку. Отменить её можно в любой момент.\n"
                                   "Каждый будний день вы будете получать актуальные курсы основных валют,"
                                   " а в пятницу недельный график")
            with open("subs.txt", "a") as s:
                s.write(str(message.from_user.id) + "\n")

        else:
            keyboard = types.InlineKeyboardMarkup()
            unsubscribe = types.InlineKeyboardButton("Отписаться", callback_data="unsub")
            keyboard.row(unsubscribe)
            await bot.send_message(message.from_user.id, "Вы уже подписаны на рассылку. Желаете отписаться от неё?",
                                   reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == "unsub")
async def val2(callback_obj: telebot.types.CallbackQuery):
    try:
        subs.remove(f"{callback_obj.from_user.id}\n")
        with open("subs.txt", "w") as s:
            for sub in subs:
                s.write(sub)
        print(subs)
        print("отписался")
        await bot.send_message(callback_obj.from_user.id, "Вы успешно отписались от рассылки")
    except Exception as ex:
        print(ex)
        await bot.send_message(callback_obj.from_user.id,
                               "Вы не можете отписаться от рассылки, так как на неё не подписаны")


@bot.callback_query_handler(func=lambda call: call.data in str1)
async def val2(callback_obj: telebot.types.CallbackQuery):
    keyboard = types.InlineKeyboardMarkup()
    usd_button = types.InlineKeyboardButton("🇺🇸 USD", callback_data="usd2")
    eur_button = types.InlineKeyboardButton("🇪🇺 EUR", callback_data="eur2")
    rub_button = types.InlineKeyboardButton("🇷🇺 RUB", callback_data="rub2")
    byn_button = types.InlineKeyboardButton("🇧🇾 BYN", callback_data="byn2")
    keyboard.row(usd_button, eur_button, rub_button, byn_button)

    # сделать словарь вместо ифов {["usd1", "usd2"]:"🇺🇸"}

    if callback_obj.data == "usd1":
        await bot.send_message(callback_obj.from_user.id, "Вы выбрали 🇺🇸")
    if callback_obj.data == "eur1":
        await bot.send_message(callback_obj.from_user.id, "Вы выбрали 🇪🇺")
    if callback_obj.data == "rub1":
        await bot.send_message(callback_obj.from_user.id, "Вы выбрали 🇷🇺")
    if callback_obj.data == "byn1":
        await bot.send_message(callback_obj.from_user.id, "Вы выбрали 🇧🇾")
    await bot.send_message(callback_obj.from_user.id, "Выберите вторую валюту", reply_markup=keyboard)
    global value1
    value1[callback_obj.from_user.id] = callback_obj.data
    print(value1)

    await bot.answer_callback_query(callback_query_id=callback_obj.id)


@bot.callback_query_handler(func=lambda call: call.data in str2)
async def calculate(callback_obj: telebot.types.CallbackQuery):
    if callback_obj.data == "usd2":
        await bot.send_message(callback_obj.from_user.id, "Вы выбрали 🇺🇸")
    if callback_obj.data == "eur2":
        await bot.send_message(callback_obj.from_user.id, "Вы выбрали 🇪🇺")
    if callback_obj.data == "rub2":
        await bot.send_message(callback_obj.from_user.id, "Вы выбрали 🇷🇺")
    if callback_obj.data == "byn2":
        await bot.send_message(callback_obj.from_user.id, "Вы выбрали 🇧🇾")
    global value2
    value2[callback_obj.from_user.id] = callback_obj.data
    print(value2)
    msg = bot.send_message(callback_obj.from_user.id, "введите сумму")
    bot.register_next_step_handler(msg, get_sum)

    await bot.answer_callback_query(callback_query_id=callback_obj.id)


async def get_sum(message):
    text = message.text
    text_er = text[:]
    v1 = value1[message.from_user.id]
    v2 = value2[message.from_user.id]
    print(v1 + v2)
    if (text.replace(".", "", 1).isdigit() or text.replace(",", "", 1).isdigit()) and len(v1) > 3 and len(v2) > 3:
        text = float(text)
        if v1[:-1] == "usd":
            text = text * (await val("USD"))
        elif v1[:-1] == "rub":
            text = text * (await val("RUB") / 100)
        elif v1[:-1] == "eur":
            text = text * (await val("EUR"))

        if v2[:-1] == "usd":
            text = text / (await val("USD"))
        elif v2[:-1] == "rub":
            text = text / (await val("RUB") / 100)
        elif v2[:-1] == "eur":
            text = text / (await val("EUR"))
        await bot.send_message(message.from_user.id,
                               f"{text_er} {v1.upper()[:-1]} = {float('{:.3f}'.format(text))} {v2.upper()[:-1]}")
    elif len(v1) < 4:
        await bot.send_message(message.from_user.id, "Вы не выбрали первую валюту")
    else:
        await bot.send_message(message.from_user.id, "Вы ввели не число\n\nПопробуйте ещё раз")


schedule.every(1).seconds.do(distribution)
loop = asyncio.get_event_loop()
while True:
    loop.run_until_complete(schedule.run_pending())
    time.sleep(0.1)
    asyncio.run(bot.polling(none_stop=True))
