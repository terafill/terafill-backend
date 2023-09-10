from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from .. import models, schemas


def get_session(db: Session, session_id: str, pruned=False):
    if pruned:
        return (
            db.query(models.Session)
            .filter(models.Session.id == session_id)
            .with_entities(
                models.Session.id,
                models.Session.client_id,
                models.Session.platform_client_id,
                models.Session.expiry_at,
                models.Session.session_token,
                models.Session.user_id,
                models.Session.activated,
            )
            .first()
        )
    return db.query(models.Session).filter(models.Session.id == session_id).first()


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
    return db_session


def expire_active_sessions(db: Session, platform_client_id: str, session_id: str):
    # Delete all sessions that match the given criteria
    db.query(models.Session).filter(
        models.Session.platform_client_id == platform_client_id,
        models.Session.id != session_id,
    ).delete()


def update_session(
    db: Session,
    db_session: schemas.Session,
    session: schemas.SessionUpdate,
):
    for field, value in session.dict(exclude_unset=True).items():
        setattr(db_session, field, value)
    return db_session
