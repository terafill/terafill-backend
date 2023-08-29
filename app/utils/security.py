import json
import logging
from datetime import datetime
from typing import Annotated, Union

from fastapi import Depends, HTTPException, status, Request, Cookie
from sqlalchemy.orm import Session

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from authlib.jose import JsonWebEncryption

from .. import crud
from ..database import get_db

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


def get_session_token(
    user_id,
    session_id,
    client_id,
    platform_client_id,
    session_private_key
):
    jwe = JsonWebEncryption()
    protected = {'alg': 'RSA-OAEP-256', 'enc': 'A256GCM'}
    payload = json.dumps({
        "userId": user_id,
        "sessionId": session_id,
        "clientId": client_id,
        "platformClientId": platform_client_id,
        "tier": "pro",
    })

    session_public_key = get_session_public_key(session_private_key)
    session_token = jwe.serialize_compact(protected, payload, session_public_key)
    return session_token.decode()


def get_session_details(session_token, session_private_key):
    jwe = JsonWebEncryption()
    data = jwe.deserialize_compact(session_token, session_private_key)
    session_details = json.loads(data["payload"].decode())
    return session_details


# Dependency to get the current user from the JWT access token
async def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    userId: Annotated[Union[str, None], Cookie()] = None,
    sessionId: Annotated[Union[str, None], Cookie()] = None,
    sessionToken: Annotated[Union[str, None], Cookie()] = None,
):
    user_id = userId
    session_id = sessionId
    session_token = sessionToken

    # Check if the user-id was provided
    if not user_id:
        raise HTTPException(status_code=401, detail="User Id missing")

    # Check if the session-id was provided
    if not session_id:
        raise HTTPException(status_code=401, detail="Session Id missing")

    # Check if the session token was provided
    if not session_token:
        raise HTTPException(status_code=401, detail="Session token missing")

    # Decode the JWE token
    try:
        db_session = crud.get_session(db, user_id, session_id)

        if db_session:
            session_details = get_session_details(session_token, db_session.session_private_key)
            if session_details["sessionId"] != session_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid Session token.",
                )

            if datetime.utcnow() > db_session.expiry_at or not db_session.activated:
                # expire active sessions which belong to specific browser/device
                crud.expire_active_sessions(
                    db,
                    user_id=session_details["userId"],
                    client_id=session_details["clientId"],
                    platform_client_id=session_details["platformClientId"],
                    session_id=session_id
                )
                raise HTTPException(
                    status_code=401,
                    detail="Session token is invalid. Token has expired or is inactive."
                )
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Invalid authentication credentials: {e}", exc_info=True)

        # Raise an HTTPException if the token is invalid
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {e}")

    else:
        return crud.get_user(db, user_id=user_id)
