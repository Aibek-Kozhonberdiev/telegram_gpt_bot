import logging
import random
import tracemalloc
import openai
import requests
import datetime
from typing import Dict
from requests import RequestException
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from config import *

tracemalloc.start()
logging.basicConfig(level=logging.INFO)

openai.api_key = GPT_KEY

USER = {}

bot = Bot(token=TELEGA_KEY)
dp = Dispatcher(bot)

kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb.add(KeyboardButton('/help - Инструкция'))

async def user(message):
    last_name = message.from_user.last_name if message.from_user.last_name is not None else ''
    first_name = message.from_user.first_name if message.from_user.first_name is not None else ''
    text = message.text
    id_ = message.from_user.id
    data = message.date
    print(f'Name: {first_name, last_name}, id: {id_}, data: {data}, text_user: {text}')
    if message.from_user.id != ADMIN:
        try:
            USER[message.from_user.id].append(f'Name: {first_name, last_name}, id: {id_}, data: {data}, text: {text}')
        except:
            USER[message.from_user.id] = []
            USER[message.from_user.id].append(f'Name: {first_name, last_name}, id: {id_}, data: {data}, text: {text}')

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer(text=random.choice(str_), reply_markup=kb)
    await user(message)

@dp.message_handler(commands=['help'])
async def send_welcome(message: types.Message):
    await message.answer(text=error1[3])
    await user(message)

@dp.message_handler(commands=['weather'])
async def weather_in(message):
    kb = InlineKeyboardMarkup(row_width=2)
    btn = InlineKeyboardButton(text='Бишкек', callback_data='btn1')
    btn1 = InlineKeyboardButton(text='Ош', callback_data='btn2')
    btn2 = InlineKeyboardButton(text='Жалалабат', callback_data='btn3')
    btn3 = InlineKeyboardButton(text='Нарын', callback_data='btn4')
    btn4 = InlineKeyboardButton(text='Каракол', callback_data='btn5')
    btn5 = InlineKeyboardButton(text='Другой город', callback_data='btn6')
    kb.add(btn, btn1, btn2, btn3, btn4, btn5)
    await message.answer('Выберите город:', reply_markup=kb)
    await user(message)

@dp.callback_query_handler()
async def check_callback_data(callback: types.CallbackQuery):
    if callback.data == 'btn1':
        choice = 'Bishkek'
    elif callback.data == 'btn2':
        choice = 'Osh'
    elif callback.data == 'btn3':
        choice = 'Jalalabat'
    elif callback.data == 'btn4':
        choice = 'Naryn'
    elif callback.data == 'btn5':
        choice = 'Karakol'
    elif callback.data == 'btn6':
        return await callback.answer(text=error1[1])
    try:
        code_to_smile = {
            "Clear": "Ясно \U00002600",
            "Clouds": "Облачно \U00002601",
            "Rain": "Дождь \U00002614",
            "Drizzle": "Дождь \U00002614",
            "Thunderstorm": "Гроза \U000026A1",
            "Snow": "Снег \U0001F328",
            "Mist": "Туман \U0001F32B"
        }

        r = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?q={choice}&appid={WEATHER_KEY}&units=metric"
        )
        data = r.json()

        city = data["name"]
        cur_weather = data["main"]["temp"]

        weather_description = data["weather"][0]["main"]
        if weather_description in code_to_smile:
            wd = code_to_smile[weather_description]
        else:
            return await callback.answer("Посмотри в окно, не пойму что там за погода!")

        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        wind = data["wind"]["speed"]
        sunrise_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunrise"])
        sunset_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunset"])
        length_of_the_day = sunset_timestamp - sunrise_timestamp

        return await callback.message.answer(
        text=f"***{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}***\n"
            f"Погода в городе: {city}\nТемпература: {cur_weather}C° {wd}\n"
            f"Влажность: {humidity}%\nДавление: {pressure} мм.рт.ст\nВетер: {wind} м/с\n"
            f"Восход солнца: {sunrise_timestamp}\nЗакат солнца: {sunset_timestamp}\nПродолжительность дня: {length_of_the_day}\n"
            f"Хорошего дня!"
        )
    except Exception as ex:
        print(f"Error: {ex}")
        return await callback.answer(text=error1[1])

@dp.message_handler(commands=['cryptocurrency'])
async def cryptocurrency(message: types.Message):
    try:
        url = 'https://api.coingecko.com/api/v3/coins/markets'
        params = {
            'vs_currency': 'usd',
            'ids': 'bitcoin,ethereum,ripple,litecoin,cardano,binancecoin,solana,dogecoin,polkadot,chainlink,aave',
            'order': 'market_cap_desc',
            'per_page': '11',
            'page': '1',
            'sparkline': 'false',
            'price_change_percentage': '24h'
        }
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        prices = {coin['symbol'].upper(): coin['current_price'] for coin in data}
        bts = []
        for symbol, price in prices.items():
            bts.append(f'{symbol}: {price}$')
        await message.answer(text='\n'.join(bts))
    except RequestException as e:
        print(f'Error: {e}')
        await message.reply(text=error1[1])
    await user(message)

@dp.message_handler(commands=['converter'])  
async def converter(message: types.Message):
    try:
        update = await message.answer('🔄Обновление данных, подождите')
        url = f"https://api.apilayer.com/exchangerates_data/convert?to=KGS&from=USD&amount=1"
        url_1 = f"https://api.apilayer.com/exchangerates_data/convert?to=KGS&from=EUR&amount=1"
        url_2 = f"https://api.apilayer.com/exchangerates_data/convert?to=KGS&from=RUB&amount=1"
        url_3 = f"https://api.apilayer.com/exchangerates_data/convert?to=KZT&from=KGS&amount=1"
        payload = {}
        headers= {
        "apikey": CONVERTER_KEY
        }
        response = requests.request("GET", url, headers=headers, data = payload)
        response_1 = requests.request("GET", url_1, headers=headers, data = payload)
        response_2 = requests.request("GET", url_2, headers=headers, data = payload)
        response_3 = requests.request("GET", url_3, headers=headers, data = payload)
        if response.status_code and response_1.status_code and response_2.status_code and response_3.status_code == 200:
            result = response.json()
            converted_price = result["result"]
            result_1 = response_1.json()
            converted_price_1 = result_1["result"]
            result_2 = response_2.json()
            converted_price_2 = result_2["result"]
            result_3 = response_3.json()
            converted_price_3 = result_3["result"]
            await message.answer(text=f"1 USD🇺🇸 = {converted_price} KGS🇰🇬\n1 EUR🇪🇺 = {converted_price_1} KGS🇰🇬\n1 RUS🇷🇺 = {converted_price_2} KGS🇰🇬\n1 KGS🇰🇬 = {converted_price_3} KZT🇰🇿")
        else:
            await message.reply("Произошла ошибка при запросе API")
    except:
        await message.reply(text=error1[2])
    await update.delete()
    await user(message)

@dp.message_handler(content_types=['video', 'photo', "voice", "audio", "video_note"])
async def none(message: types.Message):
    await message.reply("Извините, бот не обрабатывает фото, видео и аудиозаписи")
    await user(message)

@dp.message_handler(commands=['bot'])
async def user_message(message: types.Message):
    if message.from_user.id == ADMIN:
        await message.answer(text=USER)
    else:
        await message.answer("Вы не админ")
        await user(message)

async def ai(prompt):
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Уважаемый пользователь, рад приветствовать вас! Я - ChatGPT, обученный на базе GPT-3.5 архитектуры, и я готов помочь вам со всеми вопросами и задачами в моей компетенции. Буду рад оказать вам поддержку и помощь в решении любых задач. Давайте работать вместе!"},
                {"role": "user", "content": prompt}
            ]
        )

        return completion.choices[0].message.content    
    except:
        return None   

@dp.message_handler(content_types=["text"])
async def echo(message: types.Message):
    answer = await ai(message.text)
    if answer != None:
        await message.answer(text=answer)
    else:
        await message.reply(text=error1[2])
    await user(message)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates = True)
