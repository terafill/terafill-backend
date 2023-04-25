from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Column, Integer, String, ForeignKey, Enum, JSON, DateTime, LargeBinary
from sqlalchemy.orm import relationship

from ..database import Base

class Icon(Base):
    __tablename__ = "icons"
    icon_name = Column(String(255), primary_key=True, index=True)
    image = Column(LargeBinary)