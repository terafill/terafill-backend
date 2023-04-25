from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas, crud
from ..utils.security import get_current_user

router = APIRouter()

@router.get("/icons/{icon_name}")
def read_icon(icon_name: str, db: Session = Depends(get_db)):
    db_icon = db.query(models.Icon).filter(models.Icon.icon_name == icon_name).first()
    if db_icon is None:
        raise HTTPException(status_code=404, detail=f"Icon not found: {icon_name}")
    icon = schemas.Icon(icon_name=db_icon.icon_name, image=db_icon.image)
    return Response(content=icon.image, media_type="image/png")
