import uuid

from sqlalchemy.orm import Session
from sqlalchemy import and_

from .. import models, schemas


def get_item(db: Session, user_id: str, item_id: str):
    return (
        db.query(
            models.Item,
            models.CustomItemField,
        )
        .outerjoin(
            models.CustomItemField,
            and_(
                models.CustomItemField.item_id == models.Item.id,
                models.CustomItemField.user_id == models.Item.user_id,
            ),
        )
        .filter(models.Item.user_id == user_id)
        .filter(models.Item.id == item_id)
        .all()
    )


def get_item_full(db: Session, user_id: str, item_id: str):
    return (
        db.query(
            models.Item,
            models.EncryptionKey.encrypted_encryption_key,
            models.CustomItemField,
        )
        .join(
            models.EncryptionKey,
            and_(
                models.EncryptionKey.item_id == models.Item.id,
                models.EncryptionKey.user_id == models.Item.user_id,
            ),
        )
        .outerjoin(
            models.CustomItemField,
            and_(
                models.CustomItemField.item_id == models.Item.id,
                models.CustomItemField.user_id == models.Item.user_id,
            ),
        )
        .filter(models.Item.user_id == user_id)
        .filter(models.Item.id == item_id)
        .all()
    )


# def get_items(
#     db: Session, user_id: str, vault_id: str, skip: int = 0, limit: int = 100
# ):
#     return (
#         db.query(models.Item)
#         .filter(models.Item.vault_id == vault_id)
#         .filter(models.Item.user_id == user_id)
#         .offset(skip)
#         .limit(limit)
#         .all()
#     )


def get_items_full(
    db: Session, user_id: str, vault_id: str, skip: int = 0, limit: int = 100
):
    items = (
        db.query(
            models.Item,
            models.EncryptionKey.encrypted_encryption_key,
            models.CustomItemField,
        )
        .join(
            models.EncryptionKey,
            and_(
                models.EncryptionKey.item_id == models.Item.id,
                models.EncryptionKey.user_id == models.Item.user_id,
            ),
        )
        .outerjoin(
            models.CustomItemField,
            and_(
                models.CustomItemField.item_id == models.Item.id,
                models.CustomItemField.user_id == models.Item.user_id,
            ),
        )
        .filter(models.Item.vault_id == vault_id)
        .filter(models.Item.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return items


def create_item(
    db: Session,
    item: schemas.ItemCreate,
    vault_id: str,
    user_id: str,
):
    item_id = uuid.uuid4()

    db_item = models.Item(
        title=item.title,
        description=item.description,
        username=item.username,
        password=item.password,
        website=item.website,
        type=item.type,
        tags=item.tags,
        user_id=user_id,
        vault_id=vault_id,
        id=item_id,
    )
    db.add(db_item)

    custom_field_list = []
    for custom_field in item.custom_item_fields:
        custom_field_list.append(
            models.CustomItemField(
                id=uuid.uuid4(),
                field_value=custom_field.field_value,
                field_name=custom_field.field_name,
                is_tag=custom_field.is_tag,
                user_id=user_id,
                item_id=item_id,
            )
        )

    db.add_all(custom_field_list)

    return db_item, custom_field_list


def update_item(
    db: Session,
    db_item: schemas.Item,
    db_custom_item_fields,
    item: schemas.ItemUpdate,
):
    for field, value in item.dict(exclude_unset=True).items():
        setattr(db_item, field, value)

    db_field_dict = {}

    for db_custom_item_field in db_custom_item_fields:
        if db_custom_item_field:
            db_field_dict[db_custom_item_field.id] = db_custom_item_field

    add_custom_field_list = []

    for custom_item_field in item.custom_item_fields:
        action = custom_item_field.action
        if action == "CREATE":
            add_custom_field_list.append(
                models.CustomItemField(
                    id=uuid.uuid4(),
                    field_value=custom_item_field.field_value,
                    field_name=custom_item_field.field_name,
                    is_tag=custom_item_field.is_tag,
                    user_id=db_item.user_id,
                    item_id=db_item.id,
                )
            )
        elif action == "UPDATE":
            for field, value in custom_item_field.dict(exclude_unset=True).items():
                setattr(db_field_dict[str(custom_item_field.id)], field, value)
        elif action == "DELETE":
            db.delete(db_field_dict[str(custom_item_field.id)])
        else:
            # No matching action
            ...

        db.add_all(add_custom_field_list)

    return db_item


def delete_item(db: Session, db_item: schemas.Item, db_custom_item_fields):
    db.delete(db_item)
    for db_custom_item_field in db_custom_item_fields:
        if db_custom_item_field:
            db.delete(db_custom_item_field)
