import os
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
NASA_API_KEY = "YOUR_NASA_API_KEY"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def get_main_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("🌌 Фото дня", callback_data="apod")],
        [InlineKeyboardButton("☄️ Астероиды", callback_data="asteroids")],
        [InlineKeyboardButton("🚀 Фото с Марса", callback_data="mars")]
    ])
    return keyboard

@dp.message(CommandStart())
async def start_command(message: Message):
    await message.answer("Привет! Я бот NASA. Выбери, что хочешь узнать:", reply_markup=get_main_keyboard())

async def get_apod():
    url = f"https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            return data.get("url"), data.get("title"), data.get("explanation")

@dp.callback_query(F.data == "apod")
async def send_apod(callback: types.CallbackQuery):
    image_url, title, explanation = await get_apod()
    await callback.message.answer_photo(photo=image_url, caption=f"**{title}**\n\n{explanation}")

async def get_asteroids():
    url = f"https://api.nasa.gov/neo/rest/v1/feed?api_key={NASA_API_KEY}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            neo = list(data["near_earth_objects"].values())[0][0]
            return neo["name"], neo["close_approach_data"][0]["close_approach_date"], neo["nasa_jpl_url"]

@dp.callback_query(F.data == "asteroids")
async def send_asteroids(callback: types.CallbackQuery):
    name, date, link = await get_asteroids()
    await callback.message.answer(f"Ближайший астероид: **{name}**\nДата сближения: {date}\n[Подробнее]({link})", parse_mode="Markdown")

async def get_mars_photo():
    url = f"https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos?sol=1000&api_key={NASA_API_KEY}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            photo = data["photos"][0]["img_src"]
            return photo

@dp.callback_query(F.data == "mars")
async def send_mars_photo(callback: types.CallbackQuery):
    photo_url = await get_mars_photo()
    await callback.message.answer_photo(photo=photo_url, caption="Фото с Марса от ровера Curiosity!")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
