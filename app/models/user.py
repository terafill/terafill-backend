from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Column, Integer, String, Date, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base

class Gender(str, PyEnum):
    male = "male"
    female = "female"
    non_binary = "non-binary"
    transgender = "transgender"
    genderqueer = "genderqueer"
    two_spirit = "two-spirit"
    bigender = "bigender"
    pangender = "pangender"
    agender = "agender"
    demigender = "demigender"
    third_gender = "third gender"
    androgynous = "androgynous"
    intersex = "intersex"
    questioning = "questioning"
    other = "other"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    secondary_email = Column(String(255))
    phone_no = Column(String(15))
    first_name = Column(String(100))
    last_name = Column(String(100))
    birthday = Column(Date)
    gender = Column(Enum(Gender, name='gender'))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # master_password = relationship("MasterPassword", back_populates="user")
    # vaults = relationship("Vault", back_populates="user")