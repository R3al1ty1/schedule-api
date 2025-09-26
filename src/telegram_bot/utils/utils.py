import os
from dotenv import load_dotenv
from typing import Union
from aiogram.types import BufferedInputFile
from io import BytesIO
from core.db_helper import db_helper
from crud.admin import get_all_admin_user_ids
from telegram_bot.config.config import bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from sqlalchemy.ext.asyncio import AsyncSession


load_dotenv()

db = db_helper.session_getter


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
    booking_details: str,
    status: str = "approved",
    db: AsyncSession = None
) -> None:
    """
    Отправляет уведомление о новой брони пользователю в Telegram с инлайн-кнопкой на мини-приложение.
    """
    keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[
                InlineKeyboardButton(
                    text="Открыть в приложении🚀",
                    url=f"https://t.me/tavrida_schedule_bot/tavrida_schedule"
                )
            ]]
        )

    if status != "pending":
        if status == "approved":
            message = (
                "✅ <b>Одобрена новая заявка на бронирование!</b>\n\n"
                f"<b>Детали:</b>\n{booking_details}"
            )

        elif status == "rejected":
            message = (
                "❌ <b>Заявка на бронирование отклонена!</b>\n\n"
                f"<b>Детали:</b>\n{booking_details}"
            )
        elif status == "changed":
            message = (
                "✏️ <b>Заявка на бронирование изменена!</b>\n\n"
                f"<b>Детали:</b>\n{booking_details}"
            )

        await bot.send_message(
            chat_id=os.getenv("NOTIFICATIONS_CHAT_ID"),
            text=message,
            parse_mode="HTML",
            reply_markup=keyboard
        )

    else:
        message = (
            "🔔 <b>Новая заявка на бронирование!</b>\n\n"
            f"<b>Детали:</b>\n{booking_details}"
        )
        
        chat_ids = await get_all_admin_user_ids(db=db)

        for chat_id in chat_ids:
            await bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode="HTML",
                reply_markup=keyboard
            )
