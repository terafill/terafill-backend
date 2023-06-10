from datetime import datetime
from pydantic import BaseModel, UUID4


class SessionBase(BaseModel):
    session_token: str
    session_private_key: str
    csdek: UUID4
    user_id: UUID4
    client_id: UUID4
    platform_client_id: UUID4
    id: UUID4


class SessionCreate(SessionBase):
    ...

# class SessionUpdate(SessionBase):
#     ...


class Session(SessionBase):
    created_at: datetime
    expiry_at: datetime

    class Config:
        orm_mode = True
