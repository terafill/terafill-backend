import uuid

from sqlalchemy.orm import Session

from .. import models, schemas


def get_user(db: Session, user_id: str):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_sub(db: Session, sub: str):
    print("get_user_by_sub.sub", sub)
    return db.query(models.User).filter(models.User.sub == sub).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    user_id = uuid.uuid4()
    db_user = models.User(
        email=user.email,
        secondary_email=user.secondary_email,
        phone_no=user.phone_no,
        first_name=user.first_name,
        last_name=user.last_name,
        gender=user.gender,
        birthday=user.birthday,
        id=user_id,
        status=user.status,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, db_user: schemas.User, user: schemas.UserUpdate):
    for field, value in user.dict(exclude_unset=True).items():
        setattr(db_user, field, value)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, db_user: schemas.User):
    db.delete(db_user)
    db.commit()
    return db_user
