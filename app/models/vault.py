from datetime import datetime

from sqlalchemy import Column, String, ForeignKey, DateTime, JSON, Boolean, CHAR
# from sqlalchemy.orm import relationship

from ..database import Base


class Vault(Base):
    __tablename__ = "vaults"
    id = Column(CHAR(36), primary_key=True, index=True)
    name = Column(String(255), index=True)
    description = Column(String(255))
    user_id = Column(CHAR(36), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    tags = Column(JSON, nullable=True)
    is_default = Column(Boolean, default=False)