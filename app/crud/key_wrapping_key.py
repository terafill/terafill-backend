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
    db.commit()
    db.refresh(db_key_wrapping_key)
    return db_key_wrapping_key


# def update_master_password(
#     db: Session,
#     db_master_password: schemas.MasterPassword,
#     master_password: schemas.MasterPasswordUpdate,
# ):
#     for field, value in master_password.dict(exclude_unset=True).items():
#         setattr(db_master_password, field, value)
#     db.commit()
#     db.refresh(db_master_password)
#     return db_master_password


# def delete_master_password(db: Session, db_master_password: schemas.MasterPassword):
#     db.delete(db_master_password)
#     db.commit()
#     return db_master_password
