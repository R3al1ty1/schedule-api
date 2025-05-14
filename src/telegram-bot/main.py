import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, FSInputFile

# Берём токен и ссылку из .env
# TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
# MINI_APP_URL = os.getenv('MINI_APP_URL')
TOKEN="8076382500:AAGxHWo9skq81G3oVjxTQ3R3AG5RkurhAZA"
MINI_APP_URL="https://schedule-front-snowy.vercel.app/"

if not TOKEN or not MINI_APP_URL:
    raise RuntimeError("TELEGRAM_BOT_TOKEN и MINI_APP_URL должны быть заданы в окружении")

# Инициализируем бот и диспетчер
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    caption = (
        "Привет!\n"
        "Рад видеть тебя в нашем боте.\n\n"
        "Нажми на кнопку ниже, чтобы открыть мини‑приложение."
    )
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text="Открыть мини‑app", url=MINI_APP_URL)
        ]]
    )
    
    # Отправляем фото используя FSInputFile
    # try:
    #     photo = FSInputFile("tavrida.png")
    #     await message.answer_photo(
    #         photo=photo,
    #         caption=caption,
    #         reply_markup=keyboard
    #     )
    # except Exception as e:
    #     # Если возникла ошибка с фото, отправляем только текст
    #     await message.answer(
    #         text=caption,
    #         reply_markup=keyboard
    #     )

async def main():
    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
