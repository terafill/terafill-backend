from datetime import datetime, date
from enum import Enum
from typing import List, Optional
from pydantic import ConfigDict, BaseModel, EmailStr, UUID4

from app.utils.schema_helpers import to_lower_camel_case


# class Gender(str, Enum):
#     male = "male"
#     female = "female"
#     non_binary = "non-binary"
#     transgender = "transgender"
#     genderqueer = "genderqueer"
#     two_spirit = "two-spirit"
#     bigender = "bigender"
#     pangender = "pangender"
#     agender = "agender"
#     demigender = "demigender"
#     third_gender = "third gender"
#     androgynous = "androgynous"
#     intersex = "intersex"
#     questioning = "questioning"
#     other = "other"


class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    secondary_email: Optional[EmailStr] = None
    # phone_no: Optional[str] = None
    # first_name: Optional[str] = None
    # last_name: Optional[str] = None
    # birthday: Optional[date] = None
    # gender: Optional[Gender] = None
    status: Optional[str] = None
    email_verification_code: Optional[int] = None

    model_config = ConfigDict(
        from_attributes=True, alias_generator=to_lower_camel_case, populate_by_name=True
    )


class UserCreate(UserBase):
    email: EmailStr
    status: str


class UserUpdate(UserBase):
    ...
    # profile_image: Optional[bytes] = None


class UserProfileImage(UserBase):
    # profile_image: Optional[bytes] = None

    model_config = ConfigDict(from_attributes=True)


class User(UserBase):
    id: UUID4
    created_at: datetime

    # model_config = ConfigDict(from_attributes=True)
