from datetime import datetime
from typing import Optional, List

from pydantic import ConfigDict, BaseModel, UUID4

from app.utils.schema_helpers import to_lower_camel_case


class VaultBase(BaseModel):
    name: Optional[str] = None
    tags: Optional[List[str]] = None
    description: Optional[str] = None
    is_default: Optional[bool] = False

    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_lower_camel_case,
        populate_by_name=True
    )


class VaultCreate(VaultBase):
    name: str


class VaultUpdate(VaultBase):
    ...


class Vault(VaultBase):
    id: UUID4
    user_id: UUID4
    created_at: datetime
    # model_config = ConfigDict(from_attributes=True)
