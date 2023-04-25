import os
import json

from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer, HTTPBearer
from sqlalchemy.orm import Session
import jwt
import requests

from .. import crud
from ..database import db


# Dependency
def get_db():
    yield db

AWS_REGION_NAME = os.environ['AWS_REGION_NAME']
USER_POOL_ID = os.environ["USER_POOL_ID"]


security_scheme = HTTPBearer()

def get_keys():
    # Get the public keys from Amazon Cognito
    url = "https://cognito-idp.{region}.amazonaws.com/{user_pool_id}/.well-known/jwks.json".format(
        region=AWS_REGION_NAME,
        user_pool_id=USER_POOL_ID,
    )
    response = requests.get(url)
    keys = response.json()["keys"]
    return keys

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
        header = jwt.get_unverified_header(token)
        payload = jwt.decode(token, options={"verify_signature": False})
        keys = get_keys()

        kid = header["kid"]
        key = None
        for k in keys:
            if k["kid"] == kid:
                key = k
                break
        # Verify the signature of the access token using the key
        if key:
            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
            decoded_token = jwt.decode(token, public_key, algorithms=["RS256"])
        else:
            raise HTTPException(status_code=401, detail="Unable to find key to verify access token signature")
    except Exception as e:
        print(e)
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