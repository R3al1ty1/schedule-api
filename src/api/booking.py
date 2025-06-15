from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from core.consts import MAX_CAPACITY
from core.db_helper import db_helper
from core.schemas import booking as booking_schema
from core.utils import check_capacity, get_bookings_for_period, verify_admin
from crud.booking import change_booking_status, create_booking_db, create_comment_db, delete_booking_db, get_booking_by_id_db, get_bookings_db, get_calendar_data_db, update_booking_db
from core.schemas import comment as comment_schema


router = APIRouter(tags=["Bookings"])

db = db_helper.session_getter


@router.get("/bookings", response_model=booking_schema.BookingListResponse)
async def get_bookings(
    user_id: int = Header(...),
    sort_by: booking_schema.SortField = booking_schema.SortField.id,
    sort_order: booking_schema.SortOrder = booking_schema.SortOrder.desc,
    db: AsyncSession = Depends(db),
):
    """
    Получение списка бронирований.
    - Если передан user_id в заголовке, возвращает бронирования конкретного пользователя
    - Если не передан user_id, возвращает ошибку
    - Поддерживает сортировку по полям: id, start_date, end_date
    - Поддерживает порядок сортировки: asc (по возрастанию), desc (по убыванию)
    """
    
    if user_id is None:
        logger.error("Отсутствует user_id в заголовке")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Необходимо указать user_id в заголовке"
        )

    is_admin = await verify_admin(user_id, db)

    bookings = await get_bookings_db(
        db=db,
        is_admin=is_admin,
        user_id=user_id,
        sort_by=sort_by.value,
        sort_order=sort_order.value
    )

    return {"result": bookings}


@router.post("/bookings", response_model=booking_schema.Booking, status_code=status.HTTP_201_CREATED)
async def create_booking(booking: booking_schema.BookingCreate, user_id: int = Header(...), db: AsyncSession = Depends(db)):
    """
    Функция создания нового бронирования.
    Проверяет:
    - Даты начала и окончания бронирования
    - Количество людей не превышает максимальную вместимость
    - Доступность площадки на выбранные даты
    - Если бронирование успешно, сохраняет его в базе данных и отправляет уведомление
    """
    if booking.start_date > booking.end_date:
        raise HTTPException(status_code=400, detail="Дата начала должна быть раньше даты окончания")
    
    if booking.people_count > MAX_CAPACITY:
        raise HTTPException(
            status_code=400, 
            detail=f"Площадка вмещает максимум {MAX_CAPACITY} человек"
        )
    
    existing_bookings = await get_bookings_for_period(db, booking.start_date, booking.end_date)
    
    if existing_bookings:
        can_share = await check_capacity(booking, existing_bookings)
        
        if not can_share:
            raise HTTPException(
                status_code=400, 
                detail="Площадка уже забронирована на выбранные даты"
            )

    db_booking = await create_booking_db(
        db=db,
        booking=booking,
        user_id=user_id
    )

    return db_booking


@router.patch("/bookings/{booking_id}/approve", response_model=booking_schema.Booking)
async def approve_booking(
    booking_id: int,
    user_id: int = Header(...),
    db: AsyncSession = Depends(db)
):
    """
    Функция одобрения бронирования.
    Проверяет:
    - Является ли пользователь администратором
    - Существует ли бронирование с указанным ID
    - Статус бронирования должен быть "pending"
    - Проверяет доступность площадки при одобрении бронирования
    """
    check = await verify_admin(user_id, db)
    if not check:
        raise HTTPException(status_code=403, detail="Пользователь не является админом")

    booking = await get_booking_by_id_db(
        db=db,
        booking_id=booking_id
    )
    
    if not booking:
        raise HTTPException(status_code=404, detail="Бронирование не найдено")
    
    if booking.status != "pending":
        raise HTTPException(status_code=400, detail="Бронирование уже обработано")

    # Проверяем доступность площадки при одобрении бронирования
    existing_bookings = await get_bookings_for_period(db, booking.start_date, booking.end_date)
    
    if existing_bookings:
        can_share = await check_capacity(booking, existing_bookings)
        
        if not can_share:
            raise HTTPException(
                status_code=400, 
                detail="Невозможно одобрить бронирование: конфликт с существующими бронированиями"
            )

    booking = await change_booking_status(
        db=db,
        booking=booking,
        status="approved"
    )    

    return booking


@router.patch("/bookings/{booking_id}/reject", response_model=booking_schema.Booking)
async def reject_booking(
    booking_id: int,
    user_id: int = Header(...),
    db: AsyncSession = Depends(db)
):
    """
    Функция отклонения бронирования.
    Проверяет:
    - Является ли пользователь администратором
    """
    check = await verify_admin(user_id, db)
    if not check:
        raise HTTPException(status_code=403, detail="Пользователь не является админом")

    booking = await get_booking_by_id_db(
        db=db,
        booking_id=booking_id
    )
    
    if not booking:
        raise HTTPException(status_code=404, detail="Бронирование не найдено")
    
    if booking.status not in ("pending", "approved"):
        raise HTTPException(status_code=400, detail="Бронирование уже обработано")

    booking = await change_booking_status(
        db=db,
        booking=booking,
        status="rejected",
        prev_status=booking.status
    )

    return booking


@router.put("/bookings/{booking_id}", response_model=booking_schema.Booking)
async def update_booking(
    booking_id: int,
    booking_update: booking_schema.BookingUpdate,
    user_id: int = Header(...),
    db: AsyncSession = Depends(db)
):
    """
    Функция обновления бронирования.
    """
    booking = await get_booking_by_id_db(
        db=db,
        booking_id=booking_id
    )
    
    if not booking:
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
        if booking_update.people_count > MAX_CAPACITY:
            raise HTTPException(
                status_code=400, 
                detail=f"Площадка вмещает максимум {MAX_CAPACITY} человек"
            )
        booking.people_count = booking_update.people_count

    existing_bookings = await get_bookings_for_period(db, booking.start_date, booking.end_date)
    
    if existing_bookings:
        can_share = await check_capacity(booking, existing_bookings)
        
        if not can_share:
            raise HTTPException(
                status_code=400, 
                detail="Невозможно одобрить бронирование: конфликт с существующими бронированиями"
            )
    
    booking = await update_booking_db(
        db=db,
        booking=booking,
        booking_update=booking_update
    )

    return booking


@router.delete("/bookings/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_booking(
    booking_id: int,
    user_id: int = Header(...),
    db: AsyncSession = Depends(db)
):
    """
    Функция удаления бронирования.
    Проверяет:
    - Является ли пользователь администратором
    - Существует ли бронирование с указанным ID
    - Если бронирование принадлежит пользователю, который пытается его удалить
    """
    booking = await get_booking_by_id_db(
        db=db,
        booking_id=booking_id
    )
    
    if not booking:
        raise HTTPException(status_code=404, detail="Бронирование не найдено")

    is_admin = await verify_admin(user_id, db)

    if not is_admin and booking.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет прав на удаление этого бронирования"
        )
    
    await delete_booking_db(
        db=db,
        booking=booking
    )

    return


@router.get("/bookings/calendar", response_model=List[booking_schema.CalendarDay])
async def get_calendar_data(db: AsyncSession = Depends(db)):
    """
    Возвращает данные для календаря занятости за период:
    - 1 месяц назад от текущей даты
    - 4 месяца вперед от текущей даты
    """
    calendar_data = await get_calendar_data_db(db)

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
    comment: comment_schema.Comment,
    user_id: int = Header(...),
    db: AsyncSession = Depends(db)
):
    """Добавление комментария к бронированию"""
    booking = await get_booking_by_id_db(
        db=db,
        booking_id=comment.booking_id
    )
    
    if not booking:
        raise HTTPException(status_code=404, detail="Бронирование не найдено")

    is_admin = await verify_admin(user_id, db)

    if not is_admin and booking.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет прав на добавление комментария"
        )

    db_comment = await create_comment_db(
        db=db,
        comment=comment,
        booking_id=comment.booking_id
    )

    return db_comment
