from datetime import datetime, timedelta
from collections import defaultdict
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.db_helper import db_helper
from core.models import booking as booking_model
from core.schemas import booking as booking_schema
from core.utils import check_venue_availability, verify_admin
from crud.booking import get_bookings_db
from core.models import comment as comment_model
from core.schemas import comment as comment_schema


router = APIRouter(tags=["Bookings"])

db = db_helper.session_getter

@router.get("/bookings", response_model=booking_schema.BookingListResponse)
async def get_bookings(
    user_id: int = Header(...),
    db: AsyncSession = Depends(db),
):
    """
    Получение списка бронирований.
    - Если передан user_id в заголовке, возвращает бронирования конкретного пользователя
    - Если не передан user_id, возвращает ошибку
    """
    
    if user_id is None:
        logger.error("Отсутствует user_id в заголовке")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Необходимо указать user_id в заголовке"
        )

    is_admin = await verify_admin(user_id, db)

    bookings = await get_bookings_db(db=db, is_admin=is_admin, user_id=user_id)
    return {"result": bookings}


@router.post("/bookings", response_model=booking_schema.Booking, status_code=status.HTTP_201_CREATED)
async def create_booking(booking: booking_schema.BookingCreate, user_id: int = Header(...), db: AsyncSession = Depends(db)):
    if booking.start_date > booking.end_date:
        raise HTTPException(status_code=400, detail="Дата начала должна быть раньше даты окончания")
    
    MAX_CAPACITY = 300
    
    if booking.people_count > MAX_CAPACITY:
        raise HTTPException(
            status_code=400, 
            detail=f"Площадка вмещает максимум {MAX_CAPACITY} человек"
        )
    
    existing_bookings = await check_venue_availability(db, booking.start_date, booking.end_date)
    
    if existing_bookings:
        total_people = booking.people_count
        can_share = True
        
        for existing in existing_bookings:
            if existing.theme != booking.theme:
                can_share = False
                break
            total_people += existing.people_count
            if total_people > MAX_CAPACITY:
                can_share = False
                break
        
        if not can_share:
            raise HTTPException(
                status_code=400, 
                detail="Площадка уже забронирована на выбранные даты"
            )
    
    db_booking = booking_model.Booking(
        user_id=user_id,
        start_date=booking.start_date,
        end_date=booking.end_date,
        people_count=booking.people_count,
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
    
    # Перезагружаем бронирование с комментариями
    stmt = select(booking_model.Booking).where(
        booking_model.Booking.id == db_booking.id
    ).options(selectinload(booking_model.Booking.comments))
    result = await db.execute(stmt)
    db_booking = result.scalars().first()
    
    return db_booking


@router.patch("/bookings/{booking_id}/approve", response_model=booking_schema.Booking)
async def approve_booking(
    booking_id: int,
    user_id: int = Header(...),
    db: AsyncSession = Depends(db)
):
    check = await verify_admin(user_id, db)
    if not check:
        raise HTTPException(status_code=403, detail="Пользователь не является админом")

    stmt = select(booking_model.Booking).where(
        booking_model.Booking.id == booking_id
    ).options(selectinload(booking_model.Booking.comments))
    
    result = await db.execute(stmt)
    booking = result.scalars().first()
    
    if booking is None:
        raise HTTPException(status_code=404, detail="Бронирование не найдено")
    
    if booking.status != "pending":
        raise HTTPException(status_code=400, detail="Бронирование уже обработано")

    # Проверяем доступность площадки при одобрении бронирования
    existing_bookings = await check_venue_availability(db, booking.start_date, booking.end_date)
    
    if existing_bookings:
        total_people = booking.people_count
        can_share = True
        
        for existing in existing_bookings:
            if existing.theme != booking.theme:
                can_share = False
                break
            total_people += existing.people_count
            if total_people > 300:  # MAX_CAPACITY
                can_share = False
                break
        
        if not can_share:
            raise HTTPException(
                status_code=400, 
                detail="Невозможно одобрить бронирование: конфликт с существующими бронированиями"
            )
    
    booking.status = "approved"
    await db.commit()
    await db.refresh(booking)
    return booking


@router.patch("/bookings/{booking_id}/reject", response_model=booking_schema.Booking)
async def reject_booking(
    booking_id: int,
    user_id: int = Header(...),
    db: AsyncSession = Depends(db)
):
    check = await verify_admin(user_id, db)
    if not check:
        raise HTTPException(status_code=403, detail="Пользователь не является админом")
    
    stmt = select(booking_model.Booking).where(
        booking_model.Booking.id == booking_id
    ).options(selectinload(booking_model.Booking.comments))
    
    result = await db.execute(stmt)
    booking = result.scalars().first()
    
    if booking is None:
        raise HTTPException(status_code=404, detail="Бронирование не найдено")
    
    if booking.status != "pending":
        raise HTTPException(status_code=400, detail="Бронирование уже обработано")
    
    booking.status = "rejected"
    await db.commit()
    await db.refresh(booking)
    return booking


@router.put("/bookings/{booking_id}", response_model=booking_schema.Booking)
async def update_booking(
    booking_id: int,
    booking_update: booking_schema.BookingUpdate,
    user_id: int = Header(...),
    db: AsyncSession = Depends(db)
):
    stmt = select(booking_model.Booking).where(
        booking_model.Booking.id == booking_id
    ).options(selectinload(booking_model.Booking.comments))
    
    result = await db.execute(stmt)
    booking = result.scalars().first()
    
    if booking is None:
        raise HTTPException(status_code=404, detail="Бронирование не найдено")
    
    is_admin = await verify_admin(user_id, db)
    if not is_admin and booking.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет прав на изменение этого бронирования"
        )
    
    # Обновляем все поля, если они предоставлены
    if booking_update.start_date and booking_update.end_date:
        if booking_update.start_date > booking_update.end_date:
            raise HTTPException(status_code=400, detail="Дата начала должна быть раньше даты окончания")
        booking.start_date = booking_update.start_date
        booking.end_date = booking_update.end_date
    
    if booking_update.people_count:
        MAX_CAPACITY = 300
        if booking_update.people_count > MAX_CAPACITY:
            raise HTTPException(
                status_code=400, 
                detail=f"Площадка вмещает максимум {MAX_CAPACITY} человек"
            )
        booking.people_count = booking_update.people_count
    
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
    
    existing_bookings = await check_venue_availability(db, booking.start_date, booking.end_date)
    
    if existing_bookings:
        total_people = booking.people_count
        can_share = True
        
        for existing in existing_bookings:
            if existing.id != booking.id:
                if existing.theme != booking.theme:
                    can_share = False
                    break
                total_people += existing.people_count
                if total_people > MAX_CAPACITY:
                    can_share = False
                    break
        
        if not can_share:
            raise HTTPException(
                status_code=400, 
                detail="После изменений возникает конфликт с существующими бронированиями"
            )
    
    await db.commit()
    await db.refresh(booking)
    return booking


@router.delete("/bookings/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_booking(
    booking_id: int,
    user_id: int = Header(...),
    db: AsyncSession = Depends(db)
):
    stmt = select(booking_model.Booking).where(booking_model.Booking.id == booking_id)
    result = await db.execute(stmt)
    booking = result.scalars().first()
    
    if booking is None:
        raise HTTPException(status_code=404, detail="Бронирование не найдено")

    is_admin = await verify_admin(user_id, db)
    if not is_admin and booking.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет прав на удаление этого бронирования"
        )
    
    await db.delete(booking)
    await db.commit()
    return None


@router.get("/bookings/calendar", response_model=List[booking_schema.CalendarDay])
async def get_calendar_data(db: AsyncSession = Depends(db)):
    """
    Возвращает данные для календаря занятости за период:
    - 1 месяц назад от текущей даты
    - 4 месяца вперед от текущей даты
    """
    today = datetime.now().date()
    start = today - timedelta(days=120)  # месяц назад
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

    return [
        {
            "date": date,
            "total_people": data["total_people"],
            "themes": list(data["themes"])
        }
        for date, data in sorted(calendar_data.items())
    ]


@router.post("/bookings/{booking_id}/comments", response_model=comment_schema.Comment)
async def add_comment(
    booking_id: int,
    comment: comment_schema.CommentCreate,
    user_id: int = Header(...),
    db: AsyncSession = Depends(db)
):
    """Добавление комментария к бронированию"""
    # Загружаем бронирование с комментариями
    stmt = select(booking_model.Booking).where(
        booking_model.Booking.id == booking_id
    ).options(selectinload(booking_model.Booking.comments))
    
    result = await db.execute(stmt)
    booking = result.scalars().first()
    
    if booking is None:
        raise HTTPException(status_code=404, detail="Бронирование не найдено")

    is_admin = await verify_admin(user_id, db)
    if not is_admin and booking.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет прав на добавление комментария"
        )
    
    # Создаем комментарий
    db_comment = comment_model.Comment(
        comment=comment.comment,
        booking_id=booking_id
    )

    db.add(db_comment)
    await db.commit()
    await db.refresh(db_comment)
    return db_comment
