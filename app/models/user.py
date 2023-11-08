from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    Enum,
    CHAR,
    Boolean,
)
from sqlalchemy.orm import relationship

from ..database import Base


class Status(str, PyEnum):
    new_sign_up = "new_sign_up"
    unconfirmed = "unconfirmed"
    confirmed = "confirmed"
    deactivated = "deactivated"


class User(Base):
    __tablename__ = "users"
    id = Column(CHAR(36), primary_key=True, index=True)
    email_verification_code = Column(Integer)
    email = Column(CHAR(255), unique=True, index=True)
    secondary_email = Column(CHAR(255))
    email_verified = Column(Boolean)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(Enum(Status, name="status"), nullable=False)
