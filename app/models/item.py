from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Column, Integer, String, ForeignKey, Enum, JSON, DateTime
from sqlalchemy.orm import relationship

from ..database import Base

class ItemType(str, PyEnum):
    PASSWORD = "PASSWORD"
    NOTE = "NOTE"
    CREDIT_CARD = "CREDIT"
    CRYPTO_WALLET = "CRYPTO_WALLET"
    SSH_KEY = "SSH_KEY"
    SOFTWARE_LICENSE = "SOFTWARE_LICENSE"
    WIFI_PASSWORD = "WIFI_PASSWORD"
    DATABASE_CREDENTIAL = "DATABASE_CREDENTIAL"
    DOCUMENT = "DOCUMENT"

class Item(Base):
    __tablename__ = "items"
    id = Column(String(128), primary_key=True, index=True)
    title = Column(String(100), index=True)
    description = Column(String(255))
    username = Column(String(255))
    password = Column(String(255))
    website = Column(String(255))
    tags = Column(JSON, nullable=True)
    notes = Column(String(1024))
    type = Column(Enum(ItemType, name="item_type"))
    vault_id = Column(Integer, ForeignKey("vaults.id"))
    creator_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # vault = relationship("Vault", back_populates="items")
    # history = relationship("PasswordHistory", back_populates="item")
