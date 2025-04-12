from sqlalchemy import Column, Integer, String, Date, Text

from core.models.models import Base


class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    people_count = Column(Integer, nullable=False)
    event_theme = Column(String, nullable=False)
    event_description = Column(Text, nullable=True)
    status = Column(String, default="pending")
