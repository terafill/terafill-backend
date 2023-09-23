from datetime import datetime
from typing import Optional, Union, List
from pydantic import ConfigDict, BaseModel, UUID4
from enum import Enum

from app.utils.schema_helpers import to_lower_camel_case


class ItemType(str, Enum):
    PASSWORD = "PASSWORD"
    NOTE = "NOTE"
    CREDIT_CARD = "CREDIT"
    CRYPTO_WALLET = "CRYPTO_WALLET"
    SSH_KEY = "SSH_KEY"
    SOFTWARE_LICENSE = "SOFTWARE_LICENSE"
    WIFI_PASSWORD = "WIFI_PASSWORD"
    DATABASE_CREDENTIAL = "DATABASE_CREDENTIAL"
    DOCUMENT = "DOCUMENT"


class CustomItemField(BaseModel):
    field_value: str
    field_name: str
    # id: UUID4
    is_tag: bool
    model_config = ConfigDict(
        from_attributes=True, alias_generator=to_lower_camel_case, populate_by_name=True
    )


class ItemBase(BaseModel):
    title: Optional[str] = None
    description: Optional[Union[str, None]] = None
    username: Optional[str] = None
    password: Optional[str] = None
    website: Optional[str] = None
    tags: Optional[List[str]] = None
    type: Optional[ItemType] = None
    encrypted_encryption_key: Optional[str] = None
    is_favorite: Optional[bool] = False
    custom_item_fields: List[CustomItemField] = []

    model_config = ConfigDict(
        from_attributes=True, alias_generator=to_lower_camel_case, populate_by_name=True
    )


class ItemCreate(ItemBase):
    title: str


class FieldActionType(str, Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class CustomItemFieldUpdate(CustomItemField):
    action: Optional[FieldActionType] = None
    id: UUID4


class ItemUpdate(ItemBase):
    custom_item_fields: List[CustomItemFieldUpdate]
    pass


class CustomItemFieldFull(CustomItemField):
    id: UUID4


class Item(ItemBase):
    id: UUID4
    user_id: UUID4
    created_at: datetime
    vault_id: UUID4
    custom_item_fields: List[CustomItemFieldFull]
    # model_config = ConfigDict(from_attributes=True)
