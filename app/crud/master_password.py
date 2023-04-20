from sqlalchemy.orm import Session

from .. import models, schemas


def get_master_password(db: Session, user_id: int):
    return db.query(models.MasterPassword).filter(models.MasterPassword.user_id == user_id).first()


def create_master_password(
    db: Session,
    password_hash: str,
    user_id: int):
    db_master_password = models.MasterPassword(
        user_id=user_id,
        password_hash=password_hash,
        )
    db.add(db_master_password)
    db.commit()
    db.refresh(db_master_password)
    return db_master_password


def update_master_password(
        db: Session,
        db_master_password: schemas.MasterPassword,
        master_password: schemas.MasterPasswordUpdate):
    for field, value in master_password.dict(exclude_unset=True).items():
        setattr(db_master_password, field, value)
    db.commit()
    db.refresh(db_master_password)
    return db_master_password


def delete_master_password(db: Session, db_master_password: schemas.MasterPassword):
    db.delete(db_master_password)
    db.commit()
    return db_master_password