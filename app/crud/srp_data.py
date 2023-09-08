from sqlalchemy.orm import Session

from .. import models


def get_srp_data(db: Session, user_id: str, fields: list=None):
    if fields:
        return (
            db.query(*fields)
            .filter(models.SRPData.user_id == user_id)
            .first()
        )
    return db.query(models.SRPData).filter(models.SRPData.user_id == user_id).first()


def create_srp_data(db: Session, salt: str, verifier: str, user_id: str):
    db_srp_data = models.SRPData(
        user_id=user_id,
        verifier=verifier,
        salt=salt,
    )
    db.add(db_srp_data)
    return db_srp_data


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
