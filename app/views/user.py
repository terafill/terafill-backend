from typing import List, Annotated, Union
from fastapi import APIRouter, Depends, HTTPException, status, Cookie
from sqlalchemy.orm import Session

# from ..database import SessionLocal, engine
from .. import models, schemas, crud
from ..utils.security import get_current_user
from ..database import get_db


router = APIRouter(dependencies=[], tags=["user"])


@router.get("/users/me/", response_model=schemas.User, tags=["current_user"])
def read_user_me(
    current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return current_user


@router.put("/users/me/", response_model=schemas.User, tags=["current_user"])
def update_user_me(
    user: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.update_user(db=db, db_user=current_user, user=user)


# @router.delete("/users/me/", status_code=status.HTTP_204_NO_CONTENT, tags=["user"])
# def delete_user_me(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
#     return crud.delete_user(db=db, db_user=current_user)

# async def get_user_id(user_id: str = Header()):
#     return user_id

@router.post("/users/me/vaults/", response_model=schemas.Vault, tags=["current_user"])
def create_vault(
    vault: schemas.VaultCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.create_vault(db=db, vault=vault, creator_id=current_user.id)


@router.get(
    "/users/me/vaults/", response_model=List[schemas.Vault], tags=["current_user"]
)
def read_vaults(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    vaults = crud.get_vaults_by_user_id(db, user_id=current_user.id, skip=skip, limit=limit)
    return vaults


@router.get(
    "/users/me/vaults/{vault_id}", response_model=schemas.Vault, tags=["current_user"]
)
def read_vault(
    vault_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    vault = crud.get_vault(db, vault_id=vault_id)
    if vault is None:
        raise HTTPException(status_code=404, detail="Vault not found")
    return vault

# @router.post(
#     "/users/me/vaults/{vault_id}/share",
#     status_code=status.HTTP_204_NO_CONTENT,
#     tags=["current_user"]
# )
# def share_vault(
#     vault_id: str,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(get_current_user),
# ):
#     peer_user_data = crud.get_user_by_email()
#     if not peer_user_data:
#         user = schemas.UserCreate(
#             id=user_id,
#             email=email,
#             first_name=first_name,
#             last_name=last_name
#         )
#         crud.create_user(db, user)
#     vault = crud.share_vault(db, vault_id=vault_id, peer_user_id=peer_user_id)
#     if vault is None:
#         raise HTTPException(status_code=404, detail="Vault not found")
#     return vault


@router.put(
    "/users/me/vaults/{vault_id}", response_model=schemas.Vault, tags=["current_user"]
)
def update_vault(
    vault_id: str,
    vault: schemas.VaultUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_vault = crud.get_vault(db, vault_id=vault_id)
    if db_vault is None:
        raise HTTPException(status_code=404, detail="Vault not found")
    return crud.update_vault(db=db, db_vault=db_vault, vault=vault)


@router.delete(
    "/users/me/vaults/{vault_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["current_user"],
)
def delete_vault(
    vault_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_vault = crud.get_vault(db, vault_id=vault_id)
    if db_vault is None:
        raise HTTPException(status_code=404, detail="Vault not found")
    elif db_vault.is_default:
        raise HTTPException(status_code=400, detail="Default Vault cannot be delete")
    crud.delete_vault(db=db, db_vault=db_vault)


@router.post(
    "/users/me/vaults/{vault_id}/items/",
    response_model=schemas.Item,
    tags=["current_user"],
)
def create_item(
    vault_id: str,
    item: schemas.ItemCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.create_item(
        db=db, item=item, vault_id=vault_id, creator_id=current_user.id
    )


@router.get(
    "/users/me/vaults/{vault_id}/items/",
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
    items = crud.get_items(
        db, user_id=current_user.id, vault_id=vault_id, skip=skip, limit=limit
    )
    return items


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
    item = crud.get_item(
        db, user_id=current_user.id, vault_id=vault_id, item_id=item_id
    )
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


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
    db_item = crud.get_item(
        db, user_id=current_user.id, vault_id=vault_id, item_id=item_id
    )
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return crud.update_item(db=db, db_item=db_item, item=item)


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
    db_item = crud.get_item(
        db, user_id=current_user.id, vault_id=vault_id, item_id=item_id
    )
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    crud.delete_item(db=db, db_item=db_item)


@router.post("/users/me/master-password/", response_model=schemas.MasterPassword)
def create_master_password_for_user(
    master_password: schemas.MasterPasswordCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.create_master_password(
        db=db, user_id=current_user.id, password_hash=master_password.password_hash
    )


@router.get("/users/me/master-password/", response_model=schemas.MasterPassword)
def read_master_password(
    db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    master_password = crud.get_master_password(db, user_id=current_user.id)
    if master_password is None:
        raise HTTPException(status_code=404, detail="Master Password not found")
    return master_password


@router.put("/users/me/master-password/", response_model=schemas.MasterPassword)
def update_master_password(
    master_password: schemas.MasterPasswordUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_master_password = crud.get_master_password(db, user_id=current_user.id)
    if db_master_password is None:
        raise HTTPException(status_code=404, detail="Master Password not found")
    return crud.update_master_password(
        db=db, db_master_password=db_master_password, master_password=master_password
    )


@router.delete("/users/me/master-password/", status_code=status.HTTP_204_NO_CONTENT)
def delete_master_password(
    db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    db_master_password = crud.get_master_password(db, user_id=current_user.id)
    if db_master_password is None:
        raise HTTPException(status_code=404, detail="Master Password not found")
    crud.delete_master_password(db=db, db_master_password=db_master_password)


@router.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@router.get("/users/", response_model=List[schemas.User])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/users/{user_id}", response_model=schemas.User)
def read_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    user = crud.get_user(db=db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/users/{user_id}", response_model=schemas.User)
def update_user(
    user_id: str,
    user: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.update_user(db=db, db_user=db_user, user=user)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    crud.delete_user(db=db, db_user=db_user)
