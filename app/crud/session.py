from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from .. import models, schemas


def get_session(db: Session, user_id: str, session_id: str, client_id: str):
    return (
        db.query(models.Session)
        .filter(models.Session.user_id == user_id)
        .filter(models.Session.id == session_id)
        .filter(models.Session.client_id == client_id)
        .first()
    )


def create_session(db: Session, session: schemas.Session):
    created_at = datetime.utcnow()
    expiry_at = datetime.utcnow() + timedelta(hours=2)
    db_session = models.Session(
        id=session.id,
        user_id=session.user_id,
        csdek=session.csdek,
        session_private_key=session.session_private_key,
        session_token=session.session_token,
        client_id=session.client_id,
        created_at=created_at,
        expiry_at=expiry_at,
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


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
