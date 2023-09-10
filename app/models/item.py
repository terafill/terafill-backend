from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Enum,
    JSON,
    DateTime,
    CHAR,
    Boolean,
)
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
    id = Column(CHAR(36), primary_key=True, index=True)
    vault_id = Column(CHAR(36))
    user_id = Column(CHAR(36))
    title = Column(String(64))
    description = Column(String(255))
    username = Column(String(128))
    password = Column(String(128))
    website = Column(String(255))
    tags = Column(JSON, nullable=True)
    type = Column(Enum(ItemType, name="item_type"))
    is_favorite = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
