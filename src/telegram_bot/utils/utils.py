import os
from dotenv import load_dotenv
from typing import Union
from aiogram.methods import SendDocument
from aiogram import Bot
from aiogram.types import BufferedInputFile
from io import BytesIO
from telegram_bot.config.config import bot


load_dotenv()


async def send_excel_file(
    user_id: int,
    file: Union[BytesIO, bytes],
    filename: str
) -> None:
    """
    Отправляет Excel файл пользователю в Telegram.

    Args:
        bot: Экземпляр бота
        user_id: ID пользователя в Telegram
        file: Файл в формате BytesIO или bytes
        filename: Имя файла с расширением .xlsx
    """
    # Если файл передан как bytes, конвертируем его в BytesIO
    if isinstance(file, bytes):
        file_obj = BytesIO(file)
    else:
        file_obj = file
    
    # Убеждаемся, что указатель находится в начале файла
    file_obj.seek(0)
    
    # Преобразуем BytesIO в BufferedInputFile
    input_file = BufferedInputFile(
        file_obj.getvalue(),
        filename=filename
    )
    
    # Отправляем файл пользователю
    await bot.send_document(
        chat_id=user_id,
        document=input_file,
        caption="Ваш файл с расписанием 📊"
    )

async def new_booking_notification(
    booking_details: str
) -> None:
    """
    Отправляет уведомление о новой брони пользователю в Telegram.

    Args:
        user_id: ID пользователя в Telegram
        booking_details: Подробности бронирования
    """
    message = (
        "🔔 <b>Новая заявка на бронирование!</b>\n\n"
        f"<b>Детали:</b>\n{booking_details}"
    )
    await bot.send_message(
        chat_id=os.getenv("NOTIFICATIONS_CHAT_ID"),
        text=message,
        parse_mode="HTML"
    )