import uuid

from sqlalchemy.orm import Session

from .. import models, schemas


def get_user(db: Session, user_id: str):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    return db_user


def get_user_by_email(db: Session, email: str, fields: list = None):
    if fields:
        return db.query(*fields).filter(models.User.email == email).first()
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    user_id = uuid.uuid4()
    db_user = models.User(
        email=user.email,
        secondary_email=user.secondary_email,
        id=user_id,
        status=user.status,
    )
    db.add(db_user)
    return db_user


def update_user(db: Session, db_user: schemas.User, user: schemas.UserUpdate):
    for field, value in user.dict(exclude_unset=True).items():
        setattr(db_user, field, value)


def delete_user(db: Session, user_id: str):
    db.query(models.Item).filter(models.Item.user_id == user_id).delete()
    db.query(models.Vault).filter(models.Vault.user_id == user_id).delete()
    db.query(models.EncryptionKey).filter(
        models.EncryptionKey.user_id == user_id
    ).delete()
    db.query(models.KeyWrappingKey).filter(
        models.KeyWrappingKey.user_id == user_id
    ).delete()
    db.query(models.SRPData).filter(models.SRPData.user_id == user_id).delete()
    db.query(models.Session).filter(models.Session.user_id == user_id).delete()
    db.query(models.User).filter(models.User.id == user_id).delete()
