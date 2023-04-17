from typing import Optional
from datetime import datetime

from pydantic import BaseModel

class MasterPasswordBase(BaseModel):
    password_hash: str


class MasterPasswordCreate(MasterPasswordBase):
    password_hash: str

class MasterPasswordUpdate(MasterPasswordBase):
    password_hash: str


class MasterPassword(MasterPasswordBase):
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True
