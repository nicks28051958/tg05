import logging
import http.client
import os
from io import BytesIO
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram import F
from config import TOKEN, RAPIDAPI_KEY

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Создание экземпляра бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()


async def convert_to_cartoon(image_path):
    logging.info("Начинаем преобразование изображения: %s", image_path)
    conn = http.client.HTTPSConnection("cartoon-yourself.p.rapidapi.com")
    with open(image_path, 'rb') as image_file:
        payload = image_file.read()

    headers = {
        'x-rapidapi-key': RAPIDAPI_KEY,
        'x-rapidapi-host': "cartoon-yourself.p.rapidapi.com",
        'Content-Type': "application/octet-stream"
    }

    try:
        conn.request("POST", "/facebody/api/portrait-animation/portrait-animation", payload, headers)
        res = conn.getresponse()
        data = res.read()

        # Проверка статуса ответа
        if res.status != 200:
            logging.error("Ошибка при преобразовании изображения: %s", data.decode())
            return None

        logging.info("Преобразование завершено.")
        return data

    except Exception as e:
        logging.error("Произошла ошибка при запросе к API: %s", str(e))
        return None
    finally:
        conn.close()


@dp.message(Command('start'))
async def send_welcome(message: types.Message):
    await message.reply("Привет! Отправьте мне фотографию, и я сделаю её мультяшной!")


@dp.message(F.content_type == 'photo')
async def handle_photo(message: types.Message):
    logging.info("Получено фото от пользователя: %s", message.chat.id)
    photo = message.photo[-1]
    file_path = "user_photo.jpg"

    # Скачиваем файл с помощью bot.get_file
    file = await bot.get_file(photo.file_id)
    await bot.download_file(file.file_path, file_path)

    await message.reply("Преобразую ваше фото, подождите...")

    # Преобразуем фото
    cartoon_data = await convert_to_cartoon(file_path)

    if cartoon_data is None:
        await message.reply("Произошла ошибка при обработке изображения. Попробуйте еще раз.")
        return

    # Сохраняем мультяшное изображение во временный файл
    cartoon_file_path = "cartoon_photo.jpg"
    with open(cartoon_file_path, 'wb') as cartoon_file:
        cartoon_file.write(cartoon_data)

    # Отправка мультяшного изображения пользователю
    cartoon_image = types.InputFile(cartoon_file_path)
    await bot.send_photo(message.chat.id, cartoon_image)

    logging.info("Мультяшное изображение отправлено пользователю: %s", message.chat.id)

    # Удаляем временные файлы
    os.remove(file_path)
    os.remove(cartoon_file_path)


if __name__ == '__main__':
    logging.info("Запуск бота...")
    dp.run_polling(bot, skip_updates=True)
