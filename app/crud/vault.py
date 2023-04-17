from sqlalchemy.orm import Session

from .. import models, schemas


def get_vault(db: Session, vault_id: int):
    return db.query(models.Vault).filter(models.Vault.id == vault_id).first()


# def get_user_by_email(db: Session, email: str):
#     return db.query(models.User).filter(models.User.email == email).first()


def get_vaults(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Vault).offset(skip).limit(limit).all()


def create_vault(db: Session, vault: schemas.VaultCreate, current_user: schemas.User):
    db_vault = models.Vault(
        name=vault.name,
        tags=vault.tags,
        creator_id=current_user.id,
        )
    db.add(db_vault)
    db.commit()
    db.refresh(db_vault)
    return db_vault


def update_vault(db: Session, db_vault: schemas.Vault ,vault: schemas.VaultUpdate):
    for field, value in vault.dict(exclude_unset=True).items():
        setattr(db_vault, field, value)
    db.commit()
    db.refresh(db_vault)
    return db_vault


def delete_vault(db: Session, db_vault: schemas.Vault):
    db.delete(db_vault)
    db.commit()
    return db_vault