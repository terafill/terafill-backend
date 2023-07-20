from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from .. import models, schemas


def get_session(
    db: Session,
    user_id: str,
    session_id: str
):
    return (
        db.query(models.Session)
        .filter(models.Session.user_id == user_id)
        .filter(models.Session.id == session_id)
        .first()
    )


def create_session(db: Session, session: schemas.Session):
    created_at = datetime.utcnow()
    expiry_at = datetime.utcnow() + timedelta(hours=2)
    db_session = models.Session(
        id=session.id,
        user_id=session.user_id,
        session_private_key=session.session_private_key,
        session_srp_server_private_key=session.session_srp_server_private_key,
        session_srp_client_public_key=session.session_srp_client_public_key,
        session_encryption_key=session.session_encryption_key,
        session_token=session.session_token,
        client_id=session.client_id,
        platform_client_id=session.platform_client_id,
        created_at=created_at,
        expiry_at=expiry_at,
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


def expire_active_sessions(
    db: Session,
    user_id: str,
    client_id: str,
    platform_client_id: str,
    session_id: str):
    # Delete all sessions that match the given criteria
    db.query(models.Session).filter(
        models.Session.user_id == user_id,
        models.Session.client_id == client_id,
        models.Session.platform_client_id == platform_client_id,
        models.Session.id != session_id,
    ).delete()
    db.commit()

def update_session(
    db: Session,
    db_session: schemas.Session,
    session: schemas.SessionUpdate,
):
    for field, value in session.dict(exclude_unset=True).items():
        setattr(db_session, field, value)
    db.commit()
    db.refresh(db_session)
    return db_session


# def delete_master_password(db: Session, db_master_password: schemas.MasterPassword):
#     db.delete(db_master_password)
#     db.commit()
#     return db_master_password
