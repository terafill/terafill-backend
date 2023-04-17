from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas, crud
from ..utils.security import get_current_user


router = APIRouter(tags=["vault"])


@router.post("/vaults/", response_model=schemas.Vault)
def create_vault(vault: schemas.VaultCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.create_vault(db=db, vault=vault, current_user=current_user)


@router.get("/vaults/", response_model=List[schemas.Vault])
def read_vaults(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    vaults = crud.get_vaults(db, skip=skip, limit=limit)
    return vaults


@router.get("/vaults/{vault_id}", response_model=schemas.Vault)
def read_vault(vault_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    vault = crud.get_vault(db, vault_id=vault_id)
    if vault is None:
        raise HTTPException(status_code=404, detail="Vault not found")
    return vault


@router.put("/vaults/{vault_id}", response_model=schemas.Vault)
def update_vault(vault_id: int, vault: schemas.VaultUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_vault = crud.get_vault(db, vault_id=vault_id)
    if db_vault is None:
        raise HTTPException(status_code=404, detail="Vault not found")
    return crud.update_vault(db=db, db_vault=db_vault, vault=vault)


@router.delete("/vaults/{vault_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vault(vault_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_vault = crud.get_vault(db, vault_id=vault_id)
    if db_vault is None:
        raise HTTPException(status_code=404, detail="Vault not found")
    crud.delete_vault(db=db, db_vault=db_vault)
