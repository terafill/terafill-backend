from datetime import datetime
from pydantic import BaseModel, UUID4
from typing import Optional


class SessionBase(BaseModel):
    id: UUID4
    user_id: UUID4
    session_token: Optional[str] = None
    session_private_key: Optional[str] = None
    client_id: Optional[UUID4] = None
    platform_client_id: Optional[UUID4] = None
    session_encryption_key: Optional[str] = None
    session_srp_server_private_key: Optional[str] = None
    session_srp_client_public_key: Optional[str] = None
    activated: Optional[bool] = None


class SessionCreate(SessionBase):
    ...

class SessionUpdate(SessionBase):
    ...


class Session(SessionBase):
    created_at: datetime
    expiry_at: datetime

    class Config:
        orm_mode = True
