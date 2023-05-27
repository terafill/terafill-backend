from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Column, Integer, Text, Date, DateTime, Enum, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base

class Effect(str, PyEnum):
    allow = "allow"
    deny = "deny"

class UserPermission(Base):
    __tablename__ = "user_permissions"
    resource_id = Column(Text(255))
    principal_id = Column(String(128))
    user_id = Column(String(128))
    effect = Column(Enum(Effect, name='effect'))
    action = Column(Text(255))
    permission_id = Column(String(128), primary_key=True, index=True)
