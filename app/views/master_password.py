from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import SessionLocal, engine
from .. import models, schemas, crud
from ..utils.security import get_current_user, get_current_user


router = APIRouter()


# Dependency
def get_db():
    db = None
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


# @router.post("/users/{user_id}/master-passwords/", response_model=schemas.MasterPassword)
# def create_master_password_for_user(user_id: int, master_password: schemas.MasterPasswordCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
#     return crud.create_master_password_for_user(db=db, user_id=user_id, master_password=master_password)


# @router.get("/users/{user_id}/master-passwords/{master_password_id}", response_model=schemas.MasterPassword)
# def read_master_password(master_password_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
#     master_password = crud.get_master_password(db, id=master_password_id)
#     if master_password is None:
#         raise HTTPException(status_code=404, detail="Master Password not found")
#     return master_password


# @router.put("/users/{user_id}/master-passwords/{master_password_id}", response_model=schemas.MasterPassword)
# def update_master_password(master_password_id: int, master_password: schemas.MasterPasswordUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
#     db_master_password = crud.get_master_password(db, id=master_password_id)
#     if db_master_password is None:
#         raise HTTPException(status_code=404, detail="Master Password not found")
#     return crud.update_master_password(db=db, db_master_password=db_master_password, master_password=master_password)


# @router.delete("/users/{user_id}/master-passwords/{master_password_id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_master_password(master_password_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
#     db_master_password = crud.get_master_password(db, id=master_password_id)
#     if db_master_password is None:
#         raise HTTPException(status_code=404, detail="Master Password not found")
#     crud.delete_master_password(db=db, db_master_password=db_master_password)
