from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, UUID4


class VaultBase(BaseModel):
    name: Optional[str] = None
    tags: Optional[List[str]] = None
    description: Optional[str] = None
    is_default: Optional[bool] = False


class VaultCreate(VaultBase):
    name: str


class VaultUpdate(VaultBase):
    ...


class Vault(VaultBase):
    id: UUID4
    creator_id: UUID4
    created_at: datetime

    class Config:
        orm_mode = True
