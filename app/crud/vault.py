import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from .. import models, schemas


def get_vault(db: Session, user_id: str, vault_id: str):
    return (
        db.query(models.Vault)
        .filter(models.Vault.id == vault_id)
        .filter(models.Vault.user_id == user_id)
        .first()
    )


def get_vaults_by_user_id(db: Session, user_id: str, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Vault)
        .filter(models.Vault.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_vault(db: Session, vault: schemas.VaultCreate, user_id: str):
    vault_id = uuid.uuid4()
    db_vault = models.Vault(
        name=vault.name,
        tags=vault.tags,
        user_id=user_id,
        id=vault_id,
        is_default=vault.is_default,
        created_at=datetime.utcnow(),
    )
    db.add(db_vault)
    return db_vault


def update_vault(db: Session, db_vault: schemas.Vault, vault: schemas.VaultUpdate):
    for field, value in vault.dict(exclude_unset=True).items():
        setattr(db_vault, field, value)
    return db_vault


def delete_vault(db: Session, db_vault: schemas.Vault):
    db.delete(db_vault)
    return db_vault
