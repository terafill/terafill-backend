from sqlalchemy.orm import Session

from .. import models


def get_key_wrapping_key(db: Session, user_id: str):
    return (
        db.query(models.KeyWrappingKey)
        .filter(models.KeyWrappingKey.user_id == user_id)
        .first()
    )


def create_key_wrapping_key(db: Session, encrypted_key_wrapping_key: str, user_id: str):
    db_key_wrapping_key = models.KeyWrappingKey(
        user_id=user_id,
        encrypted_private_key=encrypted_key_wrapping_key,
    )
    db.add(db_key_wrapping_key)
    return db_key_wrapping_key
