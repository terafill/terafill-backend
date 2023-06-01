from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from ..database import Base


class MasterPassword(Base):
    __tablename__ = "master_passwords"
    user_id = Column(String(128), ForeignKey("users.id"), primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    password_hash = Column(String(128))
