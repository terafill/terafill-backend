from datetime import datetime
from typing import Optional, Union, List
from pydantic import BaseModel, UUID4
from enum import Enum


class IconBase(BaseModel):
    icon_name: Optional[str] = None
    image: Optional[bytes] = None


class Icon(IconBase):
    class Config:
        orm_mode = True
