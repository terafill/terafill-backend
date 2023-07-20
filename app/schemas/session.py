from datetime import datetime
from pydantic import ConfigDict, BaseModel, UUID4
from typing import Optional

from app.utils.schema_helpers import to_lower_camel_case


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

    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_lower_camel_case,
        populate_by_name=True
    )


class SessionCreate(SessionBase):
    ...

class SessionUpdate(SessionBase):
    ...


class Session(SessionBase):
    created_at: datetime
    expiry_at: datetime
    # model_config = ConfigDict(from_attributes=True)
