import base64
import logging
from typing import List, Annotated, Union

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Cookie,
    UploadFile,
    File,
    Form,
    Response,
)
from sqlalchemy.orm import Session
import requests

import app.utils.errors as internal_exceptions
from .. import models, schemas, crud
from ..utils.security import get_current_user
from ..database import get_db
from ..config import ENV


router = APIRouter(dependencies=[], tags=["user"])


@router.get("/hello")
async def hello():
    return "hello"


@router.post("/users/me/vaults", response_model=schemas.Vault, tags=["current_user"])
def create_vault(
    vault: schemas.VaultCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    try:
        vault = crud.create_vault(db=db, vault=vault, user_id=current_user.id)
        db.commit()
        return vault
    except Exception as e:
        db.rollback()
        raise internal_exceptions.InternalServerException()


@router.get(
    "/users/me/vaults", response_model=List[schemas.Vault], tags=["current_user"]
)
def read_vaults(
    response: Response,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    vaults = crud.get_vaults_by_user_id(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    return vaults


@router.get(
    "/users/me/vaults/{vault_id}", response_model=schemas.Vault, tags=["current_user"]
)
def read_vault(
    vault_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    try:
        vault = crud.get_vault(db, user_id=current_user.id, vault_id=vault_id)
        if vault is None:
            raise HTTPException(status_code=404, detail="Vault not found")
        return vault
    except HTTPException:
        raise
    except Exception as e:
        raise internal_exceptions.InternalServerException()


@router.put(
    "/users/me/vaults/{vault_id}", response_model=schemas.Vault, tags=["current_user"]
)
def update_vault(
    vault_id: str,
    vault: schemas.VaultUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        db_vault = crud.get_vault(db, user_id=current_user.id, vault_id=vault_id)
        if db_vault is None:
            raise HTTPException(status_code=404, detail="Vault not found")
        vault = crud.update_vault(db=db, db_vault=db_vault, vault=vault)
        db.commit()
        return vault
    except HTTPException:
        raise
    except Exception as e:
        raise internal_exceptions.InternalServerException()


@router.delete(
    "/users/me/vaults/{vault_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["current_user"],
)
def delete_vault(
    vault_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    try:
        db_vault = crud.get_vault(db, user_id=current_user.id, vault_id=vault_id)
        if db_vault is None:
            raise HTTPException(status_code=404, detail="Vault not found")
        elif db_vault.is_default:
            raise HTTPException(
                status_code=400, detail="Default Vault cannot be delete"
            )
        crud.delete_vault(db=db, db_vault=db_vault)
        db.commit()
    except HTTPException:
        raise
    except Exception as e:
        raise internal_exceptions.InternalServerException()


@router.post(
    "/users/me/vaults/{vault_id}/items",
    response_model=schemas.Item,
    tags=["current_user"],
)
def create_item(
    vault_id: str,
    item: schemas.ItemCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    try:
        db_item = crud.create_item(
            db=db, item=item, vault_id=vault_id, user_id=current_user.id
        )
        encrypted_encryption_key = item.encrypted_encryption_key
        crud.create_encryption_key(
            db, encrypted_encryption_key, current_user.id, db_item.id
        )
        db.commit()
        return db_item
    except HTTPException:
        db.rollback()
        logging.error(f"Error: {e}", exc_info=True)
        raise
    except Exception as e:
        db.rollback()
        logging.error(f"Error: {e}", exc_info=True)
        raise internal_exceptions.InternalServerException()


@router.get(
    "/users/me/vaults/{vault_id}/items",
    response_model=List[schemas.Item],
    tags=["current_user"],
)
def read_items(
    vault_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    try:
        results = crud.get_items_full(
            db, user_id=current_user.id, vault_id=vault_id, skip=skip, limit=limit
        )
        items = []

        for result in results:
            item, encrypted_encryption_key = result
            # item_data = item.__dict__.copy()  # this copies all the item attributes into a dictionary
            item_data = {
                k: v for k, v in item.__dict__.items() if not k.startswith("_")
            }
            item_data["encrypted_encryption_key"] = encrypted_encryption_key
            items.append(schemas.Item(**item_data))
        return items
    except HTTPException:
        logging.error(f"Error: {e}", exc_info=True)
        raise
    except Exception as e:
        logging.error(f"Error: {e}", exc_info=True)
        raise internal_exceptions.InternalServerException()


@router.get(
    "/users/me/vaults/{vault_id}/items/{item_id}",
    response_model=schemas.Item,
    tags=["current_user"],
)
def read_item(
    vault_id: str,
    item_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    try:
        result = crud.get_item_full(
            db, user_id=current_user.id, vault_id=vault_id, item_id=item_id
        )
        if result is None:
            raise HTTPException(status_code=404, detail="Item not found")

        item, encrypted_encryption_key = result
        # item_data = item.__dict__.copy()  # this copies all the item attributes into a dictionary
        item_data = {k: v for k, v in item.__dict__.items() if not k.startswith("_")}
        item_data["encrypted_encryption_key"] = encrypted_encryption_key
        item = schemas.Item(**item_data)
        return item
    except HTTPException:
        raise
    except Exception as e:
        raise internal_exceptions.InternalServerException()


@router.put(
    "/users/me/vaults/{vault_id}/items/{item_id}",
    response_model=schemas.Item,
    tags=["current_user"],
)
def update_item(
    vault_id: str,
    item_id: str,
    item: schemas.ItemUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    try:
        db_item = crud.get_item(db, user_id=current_user.id, item_id=item_id)
        if db_item is None:
            raise internal_exceptions.ItemNotFoundException()
        item = crud.update_item(db=db, db_item=db_item, item=item)
        db.commit()
        return item
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise internal_exceptions.InternalServerException()


@router.delete(
    "/users/me/vaults/{vault_id}/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["current_user"],
)
def delete_item(
    vault_id: str,
    item_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_item = crud.get_item(db, user_id=current_user.id, item_id=item_id)
    try:
        if db_item is None:
            raise internal_exceptions.ItemNotFoundException()
        crud.delete_item(db=db, db_item=db_item)
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise internal_exceptions.InternalServerException()


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    try:
        if ENV != "LOCAL":
            raise internal_exceptions.InvalidUserDeletionRequestException()
        user_id = current_user.id
        crud.delete_user(db=db, user_id=user_id)
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        logging.error(f"Error occurred: {e}", exc_info=True)
        db.rollback()
        raise internal_exceptions.InternalServerException()
