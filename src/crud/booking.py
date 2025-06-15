from collections import defaultdict
from datetime import timedelta, datetime
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.models import booking as booking_model
from core.schemas import booking as booking_schema
from core.models import comment as comment_model
from telegram_bot.utils.utils import new_booking_notification


async def get_bookings_db(
    db: AsyncSession,
    is_admin: bool = False,
    user_id: Optional[int] = None,
    sort_by: str = "id",
    sort_order: str = "asc"
) -> List[booking_schema.Booking]:
    stmt = select(booking_model.Booking).options(selectinload(booking_model.Booking.comments))
    
    if not is_admin and user_id:
        stmt = stmt.where(booking_model.Booking.user_id == user_id)
    elif not is_admin and not user_id:
        return []

    # Определяем поле для сортировки
    sort_field = getattr(booking_model.Booking, sort_by)
    
    # Применяем сортировку
    if sort_order == "desc":
        stmt = stmt.order_by(sort_field.desc())
    else:
        stmt = stmt.order_by(sort_field.asc())

    result = await db.execute(stmt)
    bookings = result.scalars().all()
    
    return [booking_schema.Booking.model_validate(b) for b in bookings]


async def create_booking_db(
    db: AsyncSession,
    booking: booking_schema.BookingCreate,
    user_id: int
) -> booking_schema.Booking:
    """
    Создает новую бронь в базе данных.
    """
    db_booking = booking_model.Booking(
        user_id=user_id,
        start_date=booking.start_date,
        end_date=booking.end_date,
        people_count=booking.people_count,
        people_count_overall=booking.people_count_overall,
        theme=booking.theme,
        description=booking.description,
        target_audience=booking.target_audience,
        name=booking.name,
        registration=booking.registration,
        logistics=booking.logistics,
        type=booking.type,
        place=booking.place,
        participants_accomodation=booking.participants_accomodation,
        experts_count=booking.experts_count,
        curator_fio=booking.curator_fio,
        curator_position=booking.curator_position,
        curator_contact=booking.curator_contact,
        other_info=booking.other_info,
        status="pending"
    )
    
    db.add(db_booking)
    await db.commit()
    await db.refresh(db_booking)

    stmt = select(booking_model.Booking).where(
        booking_model.Booking.id == db_booking.id
    ).options(selectinload(booking_model.Booking.comments))
    result = await db.execute(stmt)
    db_booking = result.scalars().first()

    return db_booking


async def change_booking_status(
    db: AsyncSession,
    booking: booking_model.Booking,
    status: str,
    prev_status: Optional[str] = None
):
    """
    Меняет статус бронирования в базе данных.
    """
    booking.status = status
    await db.commit()
    await db.refresh(booking)

    if (
        status == "approved"
        or (
            status == "rejected"
            and prev_status == "approved"
        )
    ):
        db_booking_to_send = (
            f"\n<b>Номер:</b> {booking.id}\n"
            f"<b>Даты:</b> {booking.start_date.strftime('%d.%m.%Y')} — {booking.end_date.strftime('%d.%m.%Y')}\n"
            f"<b>Название:</b> {booking.name}\n"
            f"<b>Тема:</b> {booking.theme}\n"
            f"<b>Описание:</b> {booking.description or '-'}\n"
            f"<b>Статус:</b> {booking.status}\n"
            f"<b>Количество участников с проживанием:</b> {booking.people_count}\n"
            f"<b>Количество участников и зрителей всего:</b> {booking.people_count_overall}\n"
            f"<b>Целевая аудитория:</b> {booking.target_audience or '-'}\n"
            f"<b>Тип регистрации:</b> {booking.registration or '-'}\n"
            f"<b>Логистика участников:</b> {booking.logistics or '-'}\n"
            f"<b>Тип программы:</b> {booking.type or '-'}\n"
            f"<b>Место:</b> {booking.place or '-'}\n"
            f"<b>Размещение участников:</b> {booking.participants_accomodation or '-'}\n"
            f"<b>Количество экспертов:</b> {booking.experts_count or '-'}\n"
            f"<b>Куратор:</b> {booking.curator_fio or '-'}\n"
            f"<b>Должность куратора:</b> {booking.curator_position or '-'}\n"
            f"<b>Контакты куратора:</b> {booking.curator_contact or '-'}\n"
            f"<b>Доп. информация:</b> {booking.other_info or '-'}"
        )

        await new_booking_notification(
            booking_details=db_booking_to_send
        )

    return booking


async def get_booking_by_id_db(
    db: AsyncSession,
    booking_id: int
):
    """
    Возвращает бронь по ID из базы данных.
    """
    stmt = select(booking_model.Booking).where(
        booking_model.Booking.id == booking_id
    ).options(selectinload(booking_model.Booking.comments))
    
    result = await db.execute(stmt)
    booking = result.scalars().first()

    return booking


async def update_booking_db(
    db: AsyncSession,
    booking: booking_model.Booking,
    booking_update: booking_schema.BookingUpdate
) -> booking_schema.Booking:
    """
    Обновляет бронь в базе данных.
    """
    if booking_update.theme:
        booking.theme = booking_update.theme
    
    if booking_update.description:
        booking.description = booking_update.description
        
    if booking_update.target_audience:
        booking.target_audience = booking_update.target_audience
        
    if booking_update.name:
        booking.name = booking_update.name
        
    if booking_update.registration:
        booking.registration = booking_update.registration
        
    if booking_update.logistics:
        booking.logistics = booking_update.logistics
        
    if booking_update.type:
        booking.type = booking_update.type
        
    if booking_update.place:
        booking.place = booking_update.place
        
    if booking_update.participants_accomodation:
        booking.participants_accomodation = booking_update.participants_accomodation
        
    if booking_update.experts_count:
        booking.experts_count = booking_update.experts_count
        
    if booking_update.curator_fio:
        booking.curator_fio = booking_update.curator_fio
        
    if booking_update.curator_position:
        booking.curator_position = booking_update.curator_position
        
    if booking_update.curator_contact:
        booking.curator_contact = booking_update.curator_contact
        
    if booking_update.other_info:
        booking.other_info = booking_update.other_info
    
    await db.commit()
    await db.refresh(booking)

    return booking


async def delete_booking_db(
    db: AsyncSession,
    booking: booking_model.Booking
) -> None:
    """
    Удаляет бронь из базы данных.
    """
    await db.delete(booking)
    await db.commit()


async def get_calendar_data_db(db: AsyncSession) -> dict:
    """
    Получает данные для календаря бронирований.
    """
    today = datetime.now().date()
    start = today - timedelta(days=120)  # 4 месяца назад
    end = today + timedelta(days=120)   # 4 месяца вперед
    
    # Получаем бронирования за указанный период
    stmt = select(booking_model.Booking).where(
        booking_model.Booking.end_date >= start,
        booking_model.Booking.start_date <= end,
        booking_model.Booking.status == "approved"  # Добавляем фильтр по статусу
    )

    result = await db.execute(stmt)
    bookings = result.scalars().all()

    calendar_data = defaultdict(lambda: {"total_people": 0, "themes": set()})
    
    for booking in bookings:
        current_date = max(booking.start_date, start)
        last_date = min(booking.end_date, end)
        
        delta = (last_date - current_date).days + 1
        
        for i in range(delta):
            date = current_date + timedelta(days=i)
            calendar_data[date.isoformat()]["total_people"] += booking.people_count
            calendar_data[date.isoformat()]["themes"].add(booking.theme)
    
    return calendar_data


async def create_comment_db(
    db: AsyncSession,
    booking_id: int,
    comment
):
    """
    Создает новый комментарий к бронированию.
    """
    db_comment = comment_model.Comment(
        comment=comment.comment,
        booking_id=booking_id
    )

    db.add(db_comment)
    await db.commit()
    await db.refresh(db_comment)

    return db_comment
