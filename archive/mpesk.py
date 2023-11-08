# from sqlalchemy.orm import Session

# from .. import models


# def get_mpesk(db: Session, user_id: str):
#     return (
#         db.query(models.MPESK)
#         .filter(models.MPESK.user_id == user_id)
#         .first()
#     )


# def create_mpesk(db: Session, mpesk: str, user_id: str):
#     db_master_password = models.MPESK(
#         user_id=user_id,
#         mpesk=mpesk,
#     )
#     db.add(db_master_password)
#     db.commit()
#     db.refresh(db_master_password)
#     return db_master_password


# # def update_master_password(
# #     db: Session,
# #     db_master_password: schemas.MasterPassword,
# #     master_password: schemas.MasterPasswordUpdate,
# # ):
# #     for field, value in master_password.dict(exclude_unset=True).items():
# #         setattr(db_master_password, field, value)
# #     db.commit()
# #     db.refresh(db_master_password)
# #     return db_master_password


# # def delete_master_password(db: Session, db_master_password: schemas.MasterPassword):
# #     db.delete(db_master_password)
# #     db.commit()
# #     return db_master_password
