import os
import hmac
import uuid
import random
import hashlib
import base64
import logging
from typing import Annotated, Union
from datetime import datetime

logging.basicConfig(level=logging.ERROR)


import boto3
from pydantic import ConfigDict, BaseModel, EmailStr
from sqlalchemy.orm import Session
from botocore.exceptions import ClientError
from fastapi import APIRouter, Depends, HTTPException, status, Header, Response, Cookie
from srptools import SRPServerSession, SRPContext, constants

import app.utils.errors as internal_exceptions
from app.utils.schema_helpers import to_lower_camel_case
from .. import schemas, crud
from ..database import get_db
from ..utils.errors import ErrorCodes
from ..utils.security import get_session_private_key, get_session_token, get_session_details

router = APIRouter()

# Set up AWS credentials
AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
AWS_REGION_NAME = os.environ["AWS_REGION_NAME"]


# Create a new session
session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION_NAME,
)

ses_client = session.client('ses')


class SignupRequest(BaseModel):  # Model for email verification request
    email: str

def send_verification_code(email: str, verification_code):
    sender = 'harshitsaini15@gmail.com'
    subject = 'Email Verification Code'
    message = f'Your verification code is {verification_code}'

    try:
        # Store verification code in database.
        response = ses_client.send_email(
            Destination={
                'ToAddresses': [email],
            },
            Message={
                'Body': {
                    'Text': {
                        'Charset': 'UTF-8',
                        'Data': message,
                    },
                },
                'Subject': {
                    'Charset': 'UTF-8',
                    'Data': subject,
                },
            },
            Source=sender,
        )

    except ClientError as e:
        raise internal_exceptions.InternalServerException(
            message="Something went wrong. Failed to send verification email")
    except Exception as e:
        logging.error(f"Something went wrong: {e}", exc_info=True)
        raise internal_exceptions.InternalServerException(
            message="Something went wrong. Failed to send verification email")


@router.post("/auth/signup", status_code=status.HTTP_204_NO_CONTENT, tags=["auth"])
def signup(signup_request: SignupRequest, db: Session = Depends(get_db)):
    try:
        logging.info("msgmsgmsgmsg")
        email = signup_request.email
        user_type = None

        user = crud.get_user_by_email(db, email)
        if not user:  # new user
            user_data = schemas.UserCreate(
                email=email,
                status="unconfirmed",
                first_name="",
                last_name="")
            user = crud.create_user(db, user_data)
            user_type = "new"
        else:
            user_type = user.status

        if user_type in ["new", "need_sign_up", "unconfirmed"]:  # send verification code
            verification_code = random.randint(100000, 999999)

            send_verification_code(email, verification_code)

            updated_user = schemas.UserUpdate(
                user_id=user.id,
                email_verification_code=verification_code,
                status="unconfirmed")
            crud.update_user(db=db, db_user=user, user=updated_user)

        elif user_type == "confirmed":
            raise internal_exceptions.EmailAlreadyRegisteredException()

        elif user_type == "deactivated":
            raise internal_exceptions.EmailDeactivatedException()
    except HTTPException:
        raise
    except Exception as e:
        print(f"Something went wrong {e}")
        logging.error(f"Something went wrong {e}", exc_info=True)
        raise internal_exceptions.InternalServerException()


class SignupConfirmationRequest(BaseModel):  # Model for email verification code request
    # mpesk: str
    email: str
    verification_code: str
    first_name: str
    last_name: str
    verifier: str
    salt: str
    encrypted_key_wrapping_key: str
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_lower_camel_case,
        populate_by_name=True
    )

# Endpoint for verifying email code
@router.post(
    "/auth/signup/confirm/", status_code=status.HTTP_200_OK, tags=["auth"]
)
def confirm_sign_up(
    response: Response,
    signup_confirmation_request: SignupConfirmationRequest,
    db: Session = Depends(get_db),
    client_id: Annotated[Union[str, None], Header()] = None,
    platform_client_id: Annotated[Union[str, None], Cookie()] = None
):
    try:
        email = signup_confirmation_request.email
        verification_code = signup_confirmation_request.verification_code
        # mpesk = signup_confirmation_request.mpesk
        first_name = signup_confirmation_request.first_name
        last_name = signup_confirmation_request.last_name
        verifier = signup_confirmation_request.verifier
        salt = signup_confirmation_request.salt
        encrypted_key_wrapping_key = signup_confirmation_request.encrypted_key_wrapping_key

        user = crud.get_user_by_email(db, email)

        if str(user.email_verification_code) != str(verification_code):  # verify email
            raise internal_exceptions.InvalidVerificationCodeException()

        user_id = user.id

        # Update user status and profile data
        updated_user = schemas.UserUpdate(
            first_name=first_name,
            last_name=last_name,
            status="confirmed")
        crud.update_user(db=db, db_user=user, user=updated_user)

        # # Store MPESK
        # crud.create_mpesk(db, mpesk=mpesk, user_id=user_id)

        # Store salt and verifier
        crud.create_srp_data(db, salt=salt, verifier=verifier, user_id=user_id)

        # Store salt and verifier
        crud.create_key_wrapping_key(
            db,
            encrypted_key_wrapping_key=encrypted_key_wrapping_key,
            user_id=user_id)

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Something went wrong: {e}", exc_info=True)
        raise internal_exceptions.InternalServerException()
    else:
        # Create deafult vault
        vault = schemas.VaultCreate(name="Default Vault", is_default=True)
        db_vault = crud.create_vault(db, vault, creator_id=user_id)

        # logging.error(f"created vault {user_id}", db_vault)

        # schemas.ItemCreate(
        #     title="Keylance Master Password",
        #     username=email,
        #     password=password,
        #     type="PASSWORD",
        # )
        # crud.create_item(db, item, vault_id=db_vault.id, creator_id=user_id)

        return {
        }


def build_session(
    db,
    user_id,
    client_id,
    session_srp_client_public_key,
    session_srp_server_private_key,
    session_encryption_key,
    platform_client_id=None,
    session_private_key=None,

):
    if platform_client_id is None:
        platform_client_id = str(uuid.uuid4())

    session_id = str(uuid.uuid4())

    if session_private_key is None:
        session_private_key = get_session_private_key()

    session_token = get_session_token(
        user_id,
        session_id,
        client_id,
        platform_client_id,
        session_private_key)

    # Update user status and profile data
    session = schemas.SessionCreate(
        id=session_id,
        user_id=user_id,
        session_private_key=session_private_key,
        session_token=session_token,
        client_id=client_id,
        platform_client_id=platform_client_id,
        activated=False,
        session_encryption_key=session_encryption_key,
        session_srp_server_private_key=session_srp_server_private_key,
        session_srp_client_public_key=session_srp_client_public_key,
    )
    crud.create_session(db=db, session=session)

    return {
        "sessionId": session_id,
        "sessionToken": session_token,
        "platformClientId": platform_client_id,
    }

class SaltRequest(BaseModel):
    email: EmailStr

@router.post("/auth/salt", status_code=status.HTTP_200_OK, tags=["auth"])
def get_salt(
    response: Response,
    login_request: SaltRequest,
    db: Session = Depends(get_db),
    client_id: str = Header(),
    platform_client_id: Annotated[Union[str, None], Cookie()] = None
):
    try:
        email = login_request.email

        # Get user details
        db_user = crud.get_user_by_email(db, email)
        if db_user is None:
            raise internal_exceptions.UserNotFoundException()
        user_id = db_user.id

        db_srp_data = crud.get_srp_data(db, user_id)

        salt = db_srp_data.salt

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Something went wrong: {e}", exc_info=True)
        raise internal_exceptions.InternalServerException()
    else:
        return {
            "salt": salt
        }

class LoginRequest(BaseModel):
    email: EmailStr
    client_public_key: str
    # mpesk: str
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_lower_camel_case,
        populate_by_name=True
    )


@router.post("/auth/login", status_code=status.HTTP_200_OK, tags=["auth"])
def login(
    response: Response,
    login_request: LoginRequest,
    db: Session = Depends(get_db),
    client_id: str = Header(),
    platform_client_id: Annotated[Union[str, None], Cookie()] = None
):
    try:
        email = login_request.email
        client_public_key = login_request.client_public_key

        # Get user details
        db_user = crud.get_user_by_email(db, email)
        if db_user is None:
            raise internal_exceptions.UserNotFoundException()
        user_id = db_user.id

        db_srp_data = crud.get_srp_data(db, user_id)

        verifier = db_srp_data.verifier
        salt = db_srp_data.salt

        server = SRPServerSession(SRPContext(
            username=email,
            prime=constants.PRIME_1024,
            generator=constants.PRIME_1024_GEN),
            verifier)

        server_public_key = server.public
        session_key, client_key_proof, server_key_proof =\
            server.process(client_public_key, salt)

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Something went wrong: {e}", exc_info=True)
        raise internal_exceptions.InternalServerException()
    else:
        # generate session
        session_details = build_session(
            db,
            user_id=user_id,
            client_id=client_id,
            platform_client_id=platform_client_id,
            session_encryption_key=session_key,
            session_srp_client_public_key=client_public_key,
            session_srp_server_private_key=server.private)

        # Set cookies with httpOnly flag set to true
        response.set_cookie(
            key="sessionId",
            value=session_details["sessionId"],
            httponly=True,
            max_age=7 * 24 * 60 * 60,
            secure=True,
            samesite="none"
        )
        response.set_cookie(
            key="platformClientId",
            value=session_details["platformClientId"],
            httponly=True,
            max_age=7 * 24 * 60 * 60,
            secure=True,
            samesite="none"
        )
        response.set_cookie(
            key="userId",
            value=user_id,
            httponly=False,
            max_age=7 * 24 * 60 * 60,
            secure=True,
            samesite="none"
        )
        return {
            "salt": salt,
            "serverPublicKey": server_public_key,
        }


class LoginConfirmationRequest(BaseModel):
    email: EmailStr
    client_proof: str
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_lower_camel_case,
        populate_by_name=True
    )

@router.post("/auth/login/confirm", status_code=status.HTTP_200_OK, tags=["auth"])
def login_confirm(
    response: Response,
    login_request: LoginConfirmationRequest,
    sessionId: Annotated[str, Cookie()],
    platformClientId: Annotated[str, Cookie()],
    db: Session = Depends(get_db),
    client_id: str = Header(),
):
    try:
        session_id = sessionId
        platform_client_id = platformClientId

        email = login_request.email
        client_proof = login_request.client_proof

        # Get user details
        db_user = crud.get_user_by_email(db, email)
        if db_user is None:
            raise internal_exceptions.UserNotFoundException()
        user_id = db_user.id

        db_session = crud.get_session(db, user_id, session_id)

        if db_session:
            db_srp_data = crud.get_srp_data(db, user_id)

            server = SRPServerSession(
                SRPContext(
                    username=email,
                    prime=constants.PRIME_1024,
                    generator=constants.PRIME_1024_GEN),
                db_srp_data.verifier,
                db_session.session_srp_server_private_key)

            session_key, client_key_proof, server_key_proof = \
                server.process(db_session.session_srp_client_public_key, db_srp_data.salt)

            session_details = get_session_details(
                db_session.session_token,
                db_session.session_private_key)

            if client_key_proof.decode() != client_proof:
                raise internal_exceptions.InvalidClientProofException()
        else:
            raise internal_exceptions.SessionNotFoundException()

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Something went wrong: {e}", exc_info=True)
        raise internal_exceptions.InternalServerException()
    else:
        key_wrapping_key = crud.get_key_wrapping_key(db, user_id=user_id).encrypted_private_key

        # expire active sessions
        crud.expire_active_sessions(db, user_id, client_id, platform_client_id, session_id)

        # Activate session
        session = schemas.SessionUpdate(
            id=session_id,
            user_id=user_id,
            activated=True)
        crud.update_session(db, db_session, session)

        response.set_cookie(
            key="sessionToken",
            value=db_session.session_token,
            httponly=True,
            max_age=7 * 24 * 60 * 60,
            secure=True,
            samesite="none"
        )
        return {
            "serverProof": server_key_proof,
            "keyWrappingKey": key_wrapping_key,
        }


@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT, tags=["auth"])
def logout(
    response: Response,
    db: Session = Depends(get_db),
    sessionId: str = Cookie(),
    userId: str = Cookie(),
    sessionToken: str = Cookie(),
):
    try:
        user_id = userId
        session_id = sessionId
        session_token = sessionToken

        db_session = crud.get_session(db, user_id, session_id)

        if db_session:
            session_details = get_session_details(session_token, db_session.session_private_key)
            if session_details["sessionId"] != session_id:
                raise internal_exceptions.InvalidSessionException()

            # expire active sessions which belong to specific browser/device
            crud.expire_active_sessions(
                db,
                user_id=session_details["userId"],
                client_id=session_details["clientId"],
                platform_client_id=session_details["platformClientId"],
                session_id=session_id,
            )

            response.delete_cookie("sessionToken")
            response.delete_cookie("sessionId")
            response.delete_cookie("userId")

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Something went wrong: {e}", exc_info=True)
        raise internal_exceptions.InternalServerException()


@router.post("/auth/login/refresh", status_code=status.HTTP_200_OK, tags=["auth"])
def login_refresh(
    login_request: LoginRequest,
    db: Session = Depends(get_db),
    session_id: str = Header(),
    user_id: str = Header(),
    session_token: str = Header()
):
    try:

        email = login_request.email
        mpesk = login_request.mpesk

        # Get user details
        db_user = crud.get_user_by_email(db, email)
        if db_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )
        user_id = db_user.id

        # # Get user credentials
        # db_mpesk = crud.get_mpesk(db, user_id)
        # if db_mpesk.mpesk != mpesk:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail="Incorrect username or password.",
        #     )

        db_session = crud.get_session(db, user_id, session_id)

        if db_session:
            session_details = get_session_details(session_token, db_session.session_private_key)
            if session_details["sessionId"] != session_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid Session token.",
                )

            # expire active sessions
            crud.expire_active_sessions(
                db,
                user_id=session_details["userId"],
                client_id=session_details["clientId"],
                platform_client_id=session_details["platformClientId"]
            )

            # generate session
            new_session_details = build_session(
                db,
                session_details["userId"],
                session_details["clientId"],
                session_details["platformClientId"],
                csdek=session_details["csdek"],
                session_private_key=db_session.session_private_key
            )

            return {
                "userId": user_id,
                "sessionId": new_session_details["sessionId"],
                "sessionToken": new_session_details["sessionToken"],
                "csdek": new_session_details["csdek"],
                "platformClientId": new_session_details["platformClientId"]
            }

        else:
            raise internal_exceptions.SessionNotFoundException()
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Something went wrong: {e}", exc_info=True)

        raise internal_exceptions.InternalServerException()


@router.get("/auth/status", status_code=status.HTTP_200_OK, tags=["auth"])
async def auth_status(
    response: Response,
    db: Session = Depends(get_db),
    userId: str = Cookie(),
    sessionId: str = Cookie(),
    sessionToken: str = Cookie()
):
    try:
        user_id = userId
        session_id = sessionId
        session_token = sessionToken
        db_session = crud.get_session(db, user_id, session_id)

        if db_session:
            session_details = get_session_details(session_token, db_session.session_private_key)
            if session_details["sessionId"] != session_id:
                raise internal_exceptions.InvalidSessionException()

            if datetime.utcnow() > db_session.expiry_at:
                # expire active sessions which belong to specific browser/device
                crud.expire_active_sessions(
                    db,
                    user_id=session_details["userId"],
                    client_id=session_details["clientId"],
                    platform_client_id=session_details["platformClientId"],
                    session_id=session_id,
                )

                response.delete_cookie("sessionToken")
                response.delete_cookie("sessionId")
                response.delete_cookie("userId")
                return {"loggedIn": False}

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Something went wrong: {e}", exc_info=True)
        raise internal_exceptions.InternalServerException()
    else:
        return {"loggedIn": True}
