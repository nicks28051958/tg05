import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from config import TOKEN, CURRENCY_API_KEY

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Функция для получения курсов валют
def get_currency_rates():
    url = f"https://api.currencyapi.com/v3/latest?apikey={CURRENCY_API_KEY}&currencies=EUR,USD,CAD"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Проверка на статус ответа
        data = response.json()
        rates = data['data']
        message = "Текущие курсы валют:\n"
        for currency, details in rates.items():
            message += f"{currency}: {details['value']} руб.\n"
        return message
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при получении курсов валют: {e}")
        return "Не удалось получить данные о курсе валют."

# Обработчик команды /start
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я бот для получения курсов валют. Отправьте команду /rates для просмотра курсов.")

# Обработчик команды /rates
@dp.message(Command("rates"))
async def send_rates(message: types.Message):
    rates = get_currency_rates()
    await message.reply(rates)
    await send_currency_choice(message)

# Функция для отправки выбора валюты
async def send_currency_choice(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='EUR', callback_data='currency_eur'),
            InlineKeyboardButton(text='USD', callback_data='currency_usd'),
            InlineKeyboardButton(text='CAD', callback_data='currency_cad')
        ]
    ])
    await message.reply("Выберите валюту:", reply_markup=keyboard)

# Регистрация обработчика нажатия кнопок с валютами
@dp.callback_query()
async def process_currency_choice(callback_query: CallbackQuery):
    currency = callback_query.data.split('_')[1].upper()
    logging.info(f"Пользователь выбрал валюту: {currency}")
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, f"Вы выбрали валюту: {currency}. Проверьте курсы с помощью команды /rates.")

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())




