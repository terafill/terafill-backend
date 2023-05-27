import uuid

from sqlalchemy.orm import Session

from .. import models, schemas


def get_vault(db: Session, vault_id: str):
    return db.query(models.Vault).filter(models.Vault.id == vault_id).first()


def get_all_vault_permissions_by_user_id(
    db: Session,
    user_id: str,
    skip: int = 0,
    limit: int = 100):
    return db.query(models.UserPermission)\
        .filter(models.UserPermission.user_id == user_id)\
        .offset(skip).limit(limit).all()



def get_vault_permissions_by_user_id(
    db: Session,
    user_id: str,
    vault_id: str,
    skip: int = 0,
    limit: int = 100):

    vault_level_permissions = db.query(models.UserPermission)\
        .filter(models.UserPermission.user_id == user_id)\
        .filter(models.UserPermission.resource_id in (f'krn:kps:vault:{vault_id}', 'krn:kps:vault:*'))\
        .offset(skip).limit(limit).all()

    account_level_vault_permissions = db.query(models.UserPermission)\
        .filter(models.UserPermission.user_id == user_id)\
        .filter(models.UserPermission.resource_id.like('krn:kps:account:%'))\
        .filter(models.UserPermission.action.like('vault:%'))\
        .offset(skip).limit(limit).all()

    return vault_level_permissions.union(account_level_vault_permissions)


def create_user_permission(db: Session, resource_id: str, principal_id: str, user_id: str, effect: str):
    db_user_permission = models.UserPermissions(
        resource_id=resource_id,
        principal_id=principal_id,
        user_id=user_id,
        effect=effect,
        )
    db.add(db_user_permission)
    db.commit()
    db.refresh(db_user_permission)
    return db_user_permission


def update_user_permission(db: Session, db_vault: schemas.Vault ,vault: schemas.VaultUpdate):
    for field, value in vault.dict(exclude_unset=True).items():
        setattr(db_vault, field, value)
    db.commit()
    db.refresh(db_vault)
    return db_vault


def delete_vault(db: Session, db_vault: schemas.Vault):
    db.delete(db_vault)
    db.commit()
    return db_vault