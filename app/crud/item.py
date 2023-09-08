import uuid

from sqlalchemy.orm import Session
from sqlalchemy import and_

from .. import models, schemas


def get_item(db: Session, user_id: str, vault_id: str, item_id: str):
    return (
        db.query(models.Item)
        .filter(models.Item.vault_id == vault_id)
        .filter(models.Item.creator_id == user_id)
        .filter(models.Item.id == item_id)
        .first()
    )


def get_item_full(db: Session, user_id: str, vault_id: str, item_id: str):
    return (
        db.query(models.Item, models.EncryptionKey.encrypted_encryption_key)
        .join(
            models.EncryptionKey,
            and_(
                models.EncryptionKey.user_id == models.Item.creator_id,
                models.EncryptionKey.vault_id == models.Item.vault_id,
                models.EncryptionKey.item_id == models.Item.id,
            ),
        )
        .filter(models.Item.vault_id == vault_id)
        .filter(models.Item.creator_id == user_id)
        .filter(models.Item.id == item_id)
        .first()
    )


def get_items(
    db: Session, user_id: str, vault_id: str, skip: int = 0, limit: int = 100
):
    return (
        db.query(models.Item)
        .filter(models.Item.vault_id == vault_id)
        .filter(models.Item.creator_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_items_full(
    db: Session, user_id: str, vault_id: str, skip: int = 0, limit: int = 100
):
    return (
        db.query(models.Item, models.EncryptionKey.encrypted_encryption_key)
        .join(
            models.EncryptionKey,
            and_(
                models.EncryptionKey.user_id == models.Item.creator_id,
                models.EncryptionKey.vault_id == models.Item.vault_id,
                models.EncryptionKey.item_id == models.Item.id,
            ),
        )
        .filter(models.Item.vault_id == vault_id)
        .filter(models.Item.creator_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_item(db: Session, item: schemas.ItemCreate, vault_id: str, creator_id: str):
    item_id = uuid.uuid4()

    db_item = models.Item(
        title=item.title,
        description=item.description,
        username=item.username,
        password=item.password,
        website=item.website,
        notes=item.notes,
        type=item.type,
        tags=item.tags,
        creator_id=creator_id,
        vault_id=vault_id,
        id=item_id,
    )
    db.add(db_item)
    return db_item


def update_item(db: Session, db_item: schemas.Item, item: schemas.ItemUpdate):
    for field, value in item.dict(exclude_unset=True).items():
        setattr(db_item, field, value)
    return db_item


def delete_item(db: Session, db_item: schemas.Item):
    db.delete(db_item)
    return db_item
