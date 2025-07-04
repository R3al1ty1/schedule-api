from sqlalchemy import Column, Integer, BigInteger, String, Date, Text
from sqlalchemy.orm import relationship
from core.models.models import Base


class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, index=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    people_count = Column(Integer, nullable=False)
    people_count_overall = Column(Integer, nullable=False)
    theme = Column(Text, nullable=False)  # было event_theme
    description = Column(Text)            # было event_description
    status = Column(String(50), default="pending")
    target_audience = Column(Text)
    name = Column(Text)
    registration = Column(String(10))
    logistics = Column(String(40))
    type = Column(Text)
    place = Column(Text)
    participants_accomodation = Column(Text)
    experts_count = Column(Integer)
    curator_fio = Column(Text)
    curator_position = Column(Text)
    curator_contact = Column(Text)
    other_info = Column(Text)
    
    comments = relationship("Comment", back_populates="booking", cascade="all, delete-orphan")