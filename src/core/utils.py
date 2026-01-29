import os
import hmac
import hashlib
import json
import datetime
from typing import List
from urllib.parse import unquote
from fastapi import Depends, HTTPException,  Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.consts import MAX_CAPACITY, PLACES_WITH_CAPACITY_CHECK
from core.db_helper import db_helper
from core.models.admin import Admin
from core.models import booking as booking_model
from dotenv import load_dotenv
from sqlalchemy.orm import selectinload


load_dotenv()


db = db_helper.session_getter


async def verify_admin(user_id: int, db: AsyncSession) -> bool:
    stmt = select(Admin).where(Admin.user_id == user_id)
    result = await db.execute(stmt)
    admin = result.scalars().first()

    if not admin:
        return False

    return True


async def get_bookings_for_period(
    db: AsyncSession,
    start_date: datetime,
    end_date: datetime
) -> List[booking_model.Booking]:
    """
    Проверяет существующие бронирования на указанный период времени
    """
    stmt = select(booking_model.Booking).filter(
        booking_model.Booking.status == "approved",  # Проверяем только подтвержденные бронирования
        booking_model.Booking.start_date <= end_date,  # Начало существующего <= конец нового
        booking_model.Booking.end_date >= start_date,  # Конец существующего >= начало нового
    ).options(selectinload(booking_model.Booking.comments))  # Загружаем комментарии
    
    result = await db.execute(stmt)
    existing_bookings = result.scalars().all()
    
    return existing_bookings


def verify_telegram_auth(init_data: str = Header(...)):
    """
    Проверяет подпись initData, полученную от Telegram Web App.
    """
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    secret_key = hashlib.sha256(BOT_TOKEN.encode()).digest()

    data = dict(part.split("=") for part in init_data.split("&"))
    hash_value = data.pop("hash", None)

    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(data.items()))
    calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if calculated_hash != hash_value:
        raise HTTPException(status_code=403, detail="Неверная подпись initData")

    user_str = unquote(data["user"])
    user_data = json.loads(user_str)
    user_id = user_data["id"]
    return user_id


async def check_capacity(
    booking: booking_model.Booking,
    existing_bookings: List
) -> bool:
    """
    Проверяет, можно ли совместить бронирование с существующими бронированиями.
    Проверка max_capacity выполняется только для определенных площадок.
    """
    # Проверяем, нужно ли учитывать max_capacity для данной площадки
    should_check_capacity = booking.place in PLACES_WITH_CAPACITY_CHECK

    total_people = booking.people_count
    can_share = True

    for existing in existing_bookings:
        total_people += existing.people_count
        if should_check_capacity and total_people > MAX_CAPACITY:
            can_share = False
            break

    return can_share


async def get_admin_user(
    user_id: int = Depends(verify_telegram_auth),
    db: AsyncSession = Depends(db)
):
    """
    Проверяет, является ли пользователь администратором.
    """
    is_admin = await verify_admin(user_id, db)
    if not is_admin:
        raise HTTPException(status_code=403, detail="Нет прав администратора")
    return user_id
