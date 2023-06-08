import os
import json
import logging

from fastapi import Depends, HTTPException, status, Security, Request
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
import jwt
import requests

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from authlib.jose import JsonWebEncryption

from .. import crud
from ..database import db


# Dependency
def get_db():
    yield db


AWS_REGION_NAME = os.environ["AWS_REGION_NAME"]
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

# async def get_user_id(user_id: str = Header()):
#     return user_id


# Dependency to get the current user from the JWT access token
async def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    token: str = Depends(get_token),
    # user_id: str = Depends(get_user_id),
):
    # user_id = request.headers.get('user-id')

    # Check if the token was provided
    if not token:
        raise HTTPException(status_code=401, detail="Access token missing")

    # Decode the JWT token
    try:
        header = jwt.get_unverified_header(token)
        payload = jwt.decode(token, options={"verify_signature": False})
        logging.debug("jwt payload", payload)
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
            raise HTTPException(
                status_code=401,
                detail="Unable to find key to verify access token signature",
            )
    except Exception as e:
        print(e)
        raise HTTPException(status_code=401, detail="Access token invalid")

    try:
        sub = decoded_token["sub"]
        print("USER sub", sub)
        # Return a User object with the user's data
        db_user = crud.get_user_by_sub(db, sub=sub)
        if db_user is None:
            print("db_user", db_user)
            raise HTTPException(status_code=404, detail="User not found")
        elif db_user.status != "confirmed":
            raise HTTPException(
                status_code=401,
                detail="User is either not confirmed or deactivated. Please contact support.")

        print("USER user_id", db_user.id)

        return db_user
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Invalid authentication credentials: {e}", exc_info=True)
        # Raise an HTTPException if the token is invalid
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {e}",
        )


def get_session_private_key():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # Serialize the private key in PEM format
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    session_private_key = private_key_pem.decode()

    return session_private_key


def get_session_public_key(session_private_key):
    # Load the private key from the data
    private_key = serialization.load_pem_private_key(
        session_private_key.encode(),
        password=None  # Replace with the password if the private key is encrypted
    )

    # Extract the public key from the private key
    public_key = private_key.public_key()

    # Serialize the public key in PEM format
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    session_public_key = public_key_pem.decode()

    return session_public_key


def get_session_token(user_id, session_id, client_id, session_private_key):
    jwe = JsonWebEncryption()
    protected = {'alg': 'RSA-OAEP-256', 'enc': 'A256GCM'}
    payload = json.dumps({
        "userId": user_id,
        "sessionId": session_id,
        "clientId": client_id,
        "tier": "pro",
    })

    session_public_key = get_session_public_key(session_private_key)
    session_token = jwe.serialize_compact(protected, payload, session_public_key)
    return session_token.decode()
