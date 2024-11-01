import logging
import aiohttp
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from googletrans import Translator

API_TOKEN = '7874243595:AAGLJMMYpi7X7dHrFdAPOnl4a1_nXsrLsjY'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)


async def get_joke():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://v2.jokeapi.dev/joke/Any') as response:
                joke_data = await response.json()
                if joke_data['error']:
                    logging.error(f"Ошибка при получении шутки: {joke_data['message']}")
                    return None
                if joke_data['type'] == 'single':
                    joke = joke_data['joke']
                else:
                    joke = f"{joke_data['setup']} ... {joke_data['delivery']}"

                # Переводим шутку на русский
                translator = Translator()
                translated_joke = translator.translate(joke, dest='ru').text
                return translated_joke
    except Exception as e:
        logging.error(f"Ошибка при получении шутки: {e}")
        return None

@dp.message(Command("start"))
async def send_start_message(message: types.Message):
    await message.reply("Привет! Нажмите /joke, чтобы получить шутку.")

@dp.message(Command("joke"))
async def send_joke(message: types.Message):
    joke = await get_joke()
    if joke:
        await message.reply(joke)
    else:
        await message.reply("Извините, не удалось получить шутку.")

async def main():
    await bot.delete_webhook()  # Убедитесь, что вебхук отключен
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())

