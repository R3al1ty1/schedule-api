from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo, FSInputFile
from aiogram import Router
from aiogram.filters import Command
from pathlib import Path


router = Router()

GREETING_MESSAGE = """👋 Добро пожаловать!\n
Это сервис бронирования площадок на Тавриде.\n
Пожалуйста, нажмите кнопку ниже, чтобы перейти в мини-приложение и оформить бронирование."""

keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(
            text="Открыть приложение 🚀",
            web_app=WebAppInfo(url="https://schedule-front-eight.vercel.app/")
        )]
    ]
)


@router.message(Command(commands='start'))
async def process_start_command(message: Message):
    """Обработчик команды /start."""
    # Получаем путь к изображению
    image_path = Path(__file__).parent.parent / "tavrida.png"
    photo = FSInputFile(image_path)
    
    await message.answer_photo(
        photo=photo,
        caption=GREETING_MESSAGE,
        reply_markup=keyboard
    )
