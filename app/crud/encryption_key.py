from sqlalchemy.orm import Session

from .. import models


def get_encryption_key(db: Session, user_id: str, item_id: str):
    return (
        db.query(models.EncryptionKey)
        .filter(models.EncryptionKey.item_id == item_id)
        .filter(models.EncryptionKey.user_id == user_id)
        .first()
    )


def create_encryption_key(
    db: Session, encrypted_encryption_key: str, user_id: str, item_id: str
):
    db_encryption_key = models.EncryptionKey(
        user_id=user_id,
        item_id=item_id,
        encrypted_encryption_key=encrypted_encryption_key,
    )
    db.add(db_encryption_key)
    return db_encryption_key
