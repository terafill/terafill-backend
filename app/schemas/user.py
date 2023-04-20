from datetime import datetime, date
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, EmailStr, UUID4

class Gender(str, Enum):
    male = "male"
    female = "female"
    non_binary = "non-binary"
    transgender = "transgender"
    genderqueer = "genderqueer"
    two_spirit = "two-spirit"
    bigender = "bigender"
    pangender = "pangender"
    agender = "agender"
    demigender = "demigender"
    third_gender = "third gender"
    androgynous = "androgynous"
    intersex = "intersex"
    questioning = "questioning"
    other = "other"


class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    secondary_email: Optional[EmailStr] = None
    phone_no: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birthday: Optional[date] = None
    gender: Optional[Gender] = None

class UserCreate(UserBase):
    id: UUID4
    email: EmailStr
    first_name: str

class UserUpdate(UserBase):
    pass

class User(UserBase):
    created_at: datetime

    class Config:
        orm_mode = True
