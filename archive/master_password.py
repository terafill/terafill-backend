# @router.post("/users/me/master-password/", response_model=schemas.MasterPassword)
# def create_master_password_for_user(
#     master_password: schemas.MasterPasswordCreate,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(get_current_user),
# ):
#     return crud.create_master_password(
#         db=db, user_id=current_user.id, password_hash=master_password.password_hash
#     )


# @router.get("/users/me/master-password/", response_model=schemas.MasterPassword)
# def read_master_password(
#     db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
# ):
#     master_password = crud.get_master_password(db, user_id=current_user.id)
#     if master_password is None:
#         raise HTTPException(status_code=404, detail="Master Password not found")
#     return master_password


# @router.put("/users/me/master-password/", response_model=schemas.MasterPassword)
# def update_master_password(
#     master_password: schemas.MasterPasswordUpdate,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(get_current_user),
# ):
#     db_master_password = crud.get_master_password(db, user_id=current_user.id)
#     if db_master_password is None:
#         raise HTTPException(status_code=404, detail="Master Password not found")
#     return crud.update_master_password(
#         db=db, db_master_password=db_master_password, master_password=master_password
#     )


# @router.delete("/users/me/master-password/", status_code=status.HTTP_204_NO_CONTENT)
# def delete_master_password(
#     db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
# ):
#     db_master_password = crud.get_master_password(db, user_id=current_user.id)
#     if db_master_password is None:
#         raise HTTPException(status_code=404, detail="Master Password not found")
#     crud.delete_master_password(db=db, db_master_password=db_master_password)


####### CRUD ########


# def update_master_password(
#     db: Session,
#     db_master_password: schemas.MasterPassword,
#     master_password: schemas.MasterPasswordUpdate,
# ):
#     for field, value in master_password.dict(exclude_unset=True).items():
#         setattr(db_master_password, field, value)
#     db.commit()
#     db.refresh(db_master_password)
#     return db_master_password


# def delete_master_password(db: Session, db_master_password: schemas.MasterPassword):
#     db.delete(db_master_password)
#     db.commit()
#     return db_master_password


# from sqlalchemy.orm import Session

# from .. import models, schemas


# def get_master_password(db: Session, user_id: int):
#     return (
#         db.query(models.MasterPassword)
#         .filter(models.MasterPassword.user_id == user_id)
#         .first()
#     )


# def create_master_password(db: Session, password_hash: str, user_id: int):
#     db_master_password = models.MasterPassword(
#         user_id=user_id,
#         password_hash=password_hash,
#     )
#     db.add(db_master_password)
#     db.commit()
#     db.refresh(db_master_password)
#     return db_master_password


# def update_master_password(
#     db: Session,
#     db_master_password: schemas.MasterPassword,
#     master_password: schemas.MasterPasswordUpdate,
# ):
#     for field, value in master_password.dict(exclude_unset=True).items():
#         setattr(db_master_password, field, value)
#     db.commit()
#     db.refresh(db_master_password)
#     return db_master_password


# def delete_master_password(db: Session, db_master_password: schemas.MasterPassword):
#     db.delete(db_master_password)
#     db.commit()
#     return db_master_password
