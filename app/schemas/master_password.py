from typing import Optional
from datetime import datetime

from pydantic import ConfigDict, BaseModel, UUID4


class MasterPasswordBase(BaseModel):
    password_hash: str


class MasterPasswordCreate(MasterPasswordBase):
    password_hash: str


class MasterPasswordUpdate(MasterPasswordBase):
    password_hash: str


class MasterPassword(MasterPasswordBase):
    user_id: UUID4
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
