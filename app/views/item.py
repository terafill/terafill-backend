from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import SessionLocal, engine
from .. import models, schemas, crud
from ..utils.security import get_current_user, get_current_user


router = APIRouter()


# # Dependency
# def get_db():
#     db = None
#     try:
#         db = SessionLocal()
#         yield db
#     finally:
#         db.close()


# @router.post("/items/", response_model=schemas.Item)
# def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
#     return crud.create_item(db=db, item=item)


# @router.get("/items/", response_model=List[schemas.Item])
# def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
#     items = crud.get_items(db, skip=skip, limit=limit)
#     return items


# @router.get("/items/{item_id}", response_model=schemas.Item)
# def read_item(item_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
#     item = crud.get_item_by_id(db, item_id=item_id)
#     if item is None:
#         raise HTTPException(status_code=404, detail="Item not found")
#     return item


# @router.put("/items/{item_id}", response_model=schemas.Item)
# def update_item(item_id: int, item: schemas.ItemUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
#     db_item = crud.get_item_by_id(db, item_id=item_id)
#     if db_item is None:
#         raise HTTPException(status_code=404, detail="Item not found")
#     return crud.update_item(db=db, item_id=item_id, item=item)


# @router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_item(item_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
#     db_item = crud.get_item_by_id(db, item_id=item_id)
#     if db_item is None:
#         raise HTTPException(status_code=404, detail="Item not found")
#     crud.delete_item(db=db, item_id=item_id)
