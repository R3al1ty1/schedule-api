from sqlalchemy import Column, Integer, Text, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from core.models.models import Base

class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(BigInteger, primary_key=True)
    comment = Column(Text, nullable=False)
    booking_id = Column(BigInteger, ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False)

    booking = relationship("Booking", back_populates="comments")