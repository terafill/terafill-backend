from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer, HTTPBearer
from jose import jwt, exceptions, JWTError
from sqlalchemy.orm import Session

from .. import crud
from ..database import db


# Dependency
def get_db():
    yield db


security_scheme = HTTPBearer()


# Dependency to extract the JWT access token from the HTTP request
async def get_token(token: str = Security(security_scheme)):
    if hasattr(token, "credentials"):
        return token.credentials
    return {}

# Dependency to get the current user from the JWT access token
async def get_current_user(db: Session = Depends(get_db), token: str = Depends(get_token)):

    # Check if the token was provided
    if not token:
        raise HTTPException(status_code=401, detail="Access token missing")

    # Decode the JWT token
    try:
        print("token yo! ", token)
        decoded_token = jwt.decode(token, "my_secret_key", algorithms=["HS256"])
    except JWTError:
        raise HTTPException(status_code=401, detail="Access token invalid")

    try:
        print("USER_ID", decoded_token["sub"])
        # Return a User object with the user's data
        db_user = crud.get_user(db, user_id=decoded_token["sub"])
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")

        return db_user
    except JWTError:
        # Raise an HTTPException if the token is invalid
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )