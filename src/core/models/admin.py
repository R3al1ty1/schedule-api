from sqlalchemy import Column, Integer, BigInteger

from core.models.models import Base


class Admin(Base):
    __tablename__ = "admins"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, unique=True, index=True)
