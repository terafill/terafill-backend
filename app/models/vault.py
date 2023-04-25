from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship

from ..database import Base

class Vault(Base):
    __tablename__ = "vaults"
    id = Column(String(128), primary_key=True, index=True)
    name = Column(String(100), index=True)
    description = Column(String(255))
    creator_id = Column(String(128), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    tags = Column(JSON, nullable=True)

    # user = relationship("User", back_populates="vaults")
    # items = relationship("Item", back_populates="vault")
