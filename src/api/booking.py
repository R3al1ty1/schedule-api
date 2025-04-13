from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger

from core.db_helper import db_helper
from core.schemas import booking as booking_schema
from core.models import booking as booking_model
from core.utils import check_venue_availability, get_admin_user, verify_admin, verify_telegram_auth
from crud.booking import get_bookings_db


router = APIRouter()

db = db_helper.session_getter


@router.get("/bookings", response_model=List[booking_schema.Booking])
async def get_bookings(
    user_id: int = Depends(verify_telegram_auth),
    db: AsyncSession = Depends(db)
):
    """
    Получение списка бронирований.
    - Если передан user_id в query параметрах, возвращает бронирования конкретного пользователя
    - Если не передан ни admin_id, ни user_id, возвращает ошибку
    """
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Необходимо указать либо user_id, либо admin_id в параметрах запроса"
        )

    try:
        is_admin = await verify_admin(user_id, db)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Указанный admin_id не имеет прав администратора"
        )

    return await get_bookings_db(db=db, is_admin=is_admin, user_id=user_id)


@router.post("/bookings/create", response_model=booking_schema.Booking, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking: booking_schema.BookingCreate,
    user_id: int = Depends(verify_telegram_auth),
    db: AsyncSession = Depends(db)
):
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
        logger.info(f"Проверка доступности площадки: {can_share}")
        
        for existing in existing_bookings:
            if existing.event_theme != booking.event_theme:
                logger.info(f"Первый залет: {can_share}")
                can_share = False
                break
            total_people += existing.people_count
            if total_people > MAX_CAPACITY:
                logger.info(f"Второй залет: {can_share}")
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
        event_theme=booking.event_theme,
        event_description=booking.event_description,
        status="pending"
    )
    
    db.add(db_booking)
    await db.commit()
    await db.refresh(db_booking)
    return db_booking


@router.put("/bookings/{booking_id}/approve", response_model=booking_schema.Booking)
async def approve_booking(
    booking_id: int,
    user_id: int = Depends(get_admin_user),
    db: AsyncSession = Depends(db)
):
    check = await verify_admin(user_id, db)
    if not check:
        raise HTTPException(status_code=403, detail="Пользователь не является админом")

    stmt = select(booking_model.Booking).where(booking_model.Booking.id == booking_id)
    result = await db.execute(stmt)
    booking = result.scalars().first()
    
    if booking is None:
        raise HTTPException(status_code=404, detail="Бронирование не найдено")
    
    if booking.status != "pending":
        raise HTTPException(status_code=400, detail="Бронирование уже обработано")
    
    booking.status = "approved"
    await db.commit()
    await db.refresh(booking)
    return booking


@router.put("/bookings/{booking_id}/reject", response_model=booking_schema.Booking)
async def reject_booking(
    booking_id: int,
    user_id: int = Depends(get_admin_user),
    db: AsyncSession = Depends(db)
):
    check = await verify_admin(user_id, db)
    if not check:
        raise HTTPException(status_code=403, detail="Пользователь не является админом")
    
    stmt = select(booking_model.Booking).where(booking_model.Booking.id == booking_id)
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
    user_id: int = Depends(verify_telegram_auth),
    db: AsyncSession = Depends(db)
):
    stmt = select(booking_model.Booking).where(booking_model.Booking.id == booking_id)
    result = await db.execute(stmt)
    booking = result.scalars().first()
    
    if booking is None:
        raise HTTPException(status_code=404, detail="Бронирование не найдено")
    
    check = await verify_admin(user_id, db)
    if not check:
        raise HTTPException(status_code=403, detail="Пользователь не является админом")
    
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
    
    if booking_update.event_theme:
        booking.event_theme = booking_update.event_theme
    
    if booking_update.event_description:
        booking.event_description = booking_update.event_description
    
    existing_bookings = await check_venue_availability(db, booking.start_date, booking.end_date)
    
    if existing_bookings:
        total_people = booking.people_count
        can_share = True
        
        for existing in existing_bookings:
            if existing.id != booking.id:  # Skip the current booking
                if existing.event_theme != booking.event_theme:
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
    user_id: int = Depends(verify_telegram_auth),
    db: AsyncSession = Depends(db)
):
    is_admin = await verify_admin(user_id, db)
    if not is_admin:
        raise HTTPException(status_code=403, detail="Пользователь не является админом")

    stmt = select(booking_model.Booking).where(booking_model.Booking.id == booking_id)
    result = await db.execute(stmt)
    booking = result.scalars().first()
    
    if booking is None:
        raise HTTPException(status_code=404, detail="Бронирование не найдено")

    
    if booking.user_id != user_id and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет прав на удаление этого бронирования"
        )
    
    await db.delete(booking)
    await db.commit()
    return None