from datetime import datetime
from typing import Optional, Union, List
from pydantic import BaseModel
from enum import Enum

class ItemType(str, Enum):
    PASSWORD = "PASSWORD"
    NOTE = "NOTE"
    CREDIT_CARD = "CREDIT"
    CRYPTO_WALLET = "CRYPTO_WALLET"
    SSH_KEY = "SSH_KEY"
    SOFTWARE_LICENSE = "SOFTWARE_LICENSE"
    WIFI_PASSWORD = "WIFI_PASSWORD"
    DATABASE_CREDENTIAL = "DATABASE_CREDENTIAL"
    DOCUMENT = "DOCUMENT"


class ItemBase(BaseModel):
    title: Optional[str] = None
    description: Optional[Union[str, None]] = None
    username: Optional[str] = None
    password: Optional[str] = None
    website: Optional[str] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    type: Optional[ItemType] = None


class ItemCreate(ItemBase):
    title: str

class ItemUpdate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    creator_id: int
    created_at: datetime

    class Config:
        orm_mode = True