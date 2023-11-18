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
    Request,
    Response,
)
from sqlalchemy.orm import Session
import requests

import app.utils.errors as internal_exceptions
from .. import models, schemas, crud
from ..utils.security import get_current_user
from ..database import get_db
from ..config import ENV
from ..utils.logging import logger
from ..utils.schema_helpers import orm_result_to_dict


router = APIRouter(dependencies=[], tags=["user"])


@router.get("/hello")
async def hello():
    return "hello"


@router.get("/fetch-image")
def fetch_image(url: str):
    try:
        response = requests.get(url)
        response.raise_for_status()
        mime_type = response.headers["content-type"]
        base64_image = base64.b64encode(response.content).decode("utf-8")
        return {"data_url": f"data:{mime_type};base64,{base64_image}"}
    except requests.HTTPError as e:
        raise HTTPException(status_code=400, detail="Image not found") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.post("/users/me/vaults", response_model=schemas.Vault, tags=["current_user"])
def create_vault(
    vault: schemas.VaultCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Function to create a vault"""
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
    """Function to get list of vaults"""
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
    """Function get metadata of a vault"""
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
    """Function to update a vault"""
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
    """Function to delete a vault"""
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
    """Function to create an vault item"""
    try:
        db_item, custom_field_list = crud.create_item(
            db=db, item=item, vault_id=vault_id, user_id=current_user.id
        )
        encrypted_encryption_key = item.encrypted_encryption_key
        crud.create_encryption_key(
            db, encrypted_encryption_key, current_user.id, db_item.id
        )
        db.commit()
        db_item.custom_item_fields = custom_field_list
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
    """Function to fetch list of items belonging to a vault"""
    try:
        results = crud.get_items_full(
            db, user_id=current_user.id, vault_id=vault_id, skip=skip, limit=limit
        )
        item_dict = {}

        for item_data in results:
            item, encrypted_encryption_key, custom_item_fields = item_data
            if item.id not in item_dict:
                item_dict[item.id] = orm_result_to_dict(item)
                item_dict[item.id][
                    "encrypted_encryption_key"
                ] = encrypted_encryption_key
                item_dict[item.id]["custom_item_fields"] = []

            if custom_item_fields:
                item_dict[item.id]["custom_item_fields"].append(
                    orm_result_to_dict(custom_item_fields)
                )
        items = []
        for item_data in item_dict.values():
            items.append(schemas.Item(**item_data))
        return items
    except HTTPException:
        logging.error(f"Error: {e}", exc_info=True)
        raise
    except Exception as e:
        logging.error(f"Error: {e}", exc_info=True)
        raise internal_exceptions.InternalServerException()


@router.get(
    "/users/me/tags/{tag_id}/items",
    response_model=List[schemas.Item],
    tags=["current_user"],
)
def read_items_by_tag_id(
    tag_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Function to fetch list of items related to given tag-id"""
    try:
        results = crud.get_items_full_by_tag_id(
            db, user_id=current_user.id, tag_id=tag_id, skip=skip, limit=limit
        )
        item_dict = {}

        for item_data in results:
            item, encrypted_encryption_key, custom_item_fields = item_data
            if item.id not in item_dict:
                item_dict[item.id] = orm_result_to_dict(item)
                item_dict[item.id][
                    "encrypted_encryption_key"
                ] = encrypted_encryption_key
                item_dict[item.id]["custom_item_fields"] = []

            if custom_item_fields:
                item_dict[item.id]["custom_item_fields"].append(
                    orm_result_to_dict(custom_item_fields)
                )
        items = []
        for item_data in item_dict.values():
            items.append(schemas.Item(**item_data))
        return items
    except HTTPException:
        logging.error(f"Error: {e}", exc_info=True)
        raise
    except Exception as e:
        logging.error(f"Error: {e}", exc_info=True)
        raise internal_exceptions.InternalServerException()


@router.get(
    "/users/me/tags",
    # response_model=List[schemas.Item],
    tags=["current_user"],
)
def read_tags(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Function to fetch list of tags/labels"""
    try:
        result = crud.get_tags(db, user_id=current_user.id, skip=skip, limit=limit)
        if result:
            return list(map(lambda x: x["field_value"], result))
        return []
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
    """Function to fetch vault item data"""
    try:
        result = crud.get_item_full(db, user_id=current_user.id, item_id=item_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Item not found")

        item, encrypted_encryption_key, custom_item_fields = result[0]

        item_dict = orm_result_to_dict(item)
        item_dict["encrypted_encryption_key"] = encrypted_encryption_key
        item_dict["custom_item_fields"] = []

        for item_data in result:
            item, encrypted_encryption_key, custom_item_fields = item_data
            if custom_item_fields:
                item_dict["custom_item_fields"].append(
                    orm_result_to_dict(custom_item_fields)
                )

        item = schemas.Item(**item_dict)
        return item
    except HTTPException:
        logging.error(f"Error: {e}", exc_info=True)
        raise
    except Exception as e:
        logging.error(f"Error: {e}", exc_info=True)
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
    """Function to update a vault item"""
    try:
        results = crud.get_item(db, user_id=current_user.id, item_id=item_id)
        if results is None:
            raise internal_exceptions.ItemNotFoundException()

        db_item_list, db_custom_item_fields = list(zip(*results))

        item = crud.update_item(
            db=db,
            db_item=db_item_list[0],
            db_custom_item_fields=db_custom_item_fields,
            item=item,
        )
        db.commit()
        return item
    except HTTPException as e:
        logger.exception(f"An error occurred: {str(e)}", exc_info=True)
        db.rollback()
        raise
    except Exception as e:
        logger.exception(f"An error occurred: {str(e)}", exc_info=True)
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
    """Function to delete a vault item"""
    results = crud.get_item(db, user_id=current_user.id, item_id=item_id)
    try:
        if results is None:
            raise internal_exceptions.ItemNotFoundException()
        db_item_list, db_custom_item_fields = list(zip(*results))

        crud.delete_item(
            db=db, db_item=db_item_list[0], db_custom_item_fields=db_custom_item_fields
        )
        db.commit()
    except HTTPException as e:
        logger.exception(f"An error occurred: {str(e)}", exc_info=True)
        db.rollback()
        raise
    except Exception as e:
        logger.exception(f"An error occurred: {str(e)}", exc_info=True)
        db.rollback()
        raise internal_exceptions.InternalServerException()


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Function to delete a user. Only applicable in local environments."""
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
