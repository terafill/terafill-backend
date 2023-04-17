from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

class VaultBase(BaseModel):
    name: Optional[str] = None
    tags: Optional[List[str]] = None
    description: Optional[str] = None

class VaultCreate(VaultBase):
    name: str

class VaultUpdate(VaultBase):
    ...


class Vault(VaultBase):
    id: int
    creator_id: int
    created_at: datetime
    class Config:
        orm_mode = True
