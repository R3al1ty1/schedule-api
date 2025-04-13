from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime

# Схема для входящих данных при создании бронирования: поля id, status и user_id не нужны.
class BookingCreate(BaseModel):
    start_date: datetime
    end_date: datetime
    people_count: int
    event_theme: str
    event_description: Optional[str] = None

    class Config:
        json_encoders = {
            date: lambda v: v.strftime('%Y-%m-%d')
        }

# Схема для обновления бронирования — все поля необязательны
class BookingUpdate(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    people_count: Optional[int] = None
    event_theme: Optional[str] = None
    event_description: Optional[str] = None

# Схема для чтения (ответ) с сервера, включает служебные поля
class Booking(BaseModel):
    id: int
    user_id: int
    start_date: date
    end_date: date
    people_count: int
    event_theme: str
    event_description: Optional[str] = None
    status: str
    
    model_config = {
        "from_attributes": True  # Аналог orm_mode для Pydantic v2
    }

# Если нужна схема для запроса списка бронирований по admin_id
class BookingListRequest(BaseModel):
    admin_id: Optional[int] = None


class BookingListResponse(BaseModel):
    result: List[Booking]


class CalendarDay(BaseModel):
    date: str
    total_people: int
    themes: List[str]
