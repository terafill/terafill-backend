from datetime import datetime
from typing import Optional, List
from enum import Enum

from pydantic import BaseModel, UUID4

class Effect(str, Enum):
    allow = "allow"
    deny = "deny"

class UserPermissionBase(BaseModel):
    effect: Effect

class UserPermissionCreate(UserPermissionBase):
    resource_id: str
    principal_id: UUID4
    user_id: UUID4
    action: str
    permission_id: UUID4

class UserPermissionUpdate(UserPermissionBase):
    ...

class UserPermission(UserPermissionBase):
    resource_id: str
    principal_id: UUID4
    user_id: UUID4
    action: str
    permission_id: UUID4
    class Config:
        orm_mode = True
