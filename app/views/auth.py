import os
import hmac
import uuid
import random
import hashlib
import base64
import logging
from typing import Annotated, Union
from datetime import datetime

import boto3
from pydantic import BaseModel
from sqlalchemy.orm import Session
from botocore.exceptions import ClientError
from fastapi import APIRouter, Depends, HTTPException, status, Header, Response, Cookie


from .. import schemas, crud
from ..database import get_db
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


class SignupConfirmationRequest(BaseModel):  # Model for email verification code request
    email: str
    mpesk: str
    verification_code: str
    first_name: str
    last_name: str


def get_secret_hash(username, client_id, client_secret):
    message = username + client_id
    digest = hmac.new(
        str(client_secret).encode("utf-8"),
        msg=message.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).digest()
    return base64.b64encode(digest).decode()


def send_verification_code(email, verification_code):
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
        # print(response)

    except ClientError as e:
        print(e.response['Error']['Message'])
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email")
    except Exception as e:
        logging.error(f"Something went wrong: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email")


@router.post("/auth/signup/", status_code=status.HTTP_204_NO_CONTENT, tags=["auth"])
def signup(signup_request: SignupRequest, db: Session = Depends(get_db)):
    try:
        email = signup_request.email
        user_type = None

        user = crud.get_user_by_email(db, email)
        if not user:  # new user
            user_data = schemas.UserCreate(
                email=email,
                status="unconfirmed")
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
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email is already registered.",
            )
        elif user_type == "deactivated":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email is deactivated. Please contact support for resolution.",
            )
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Something went wrong {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Something went wrong. Please try again.",
        )


def build_session(
    db,
    user_id,
    client_id,
    platform_client_id=None,
    csdek=None,
    session_private_key=None
):

    session_id = str(uuid.uuid4())

    if platform_client_id is None:
        platform_client_id = str(uuid.uuid4())

    if csdek is None:
        csdek = str(uuid.uuid4())

    if session_private_key is None:
        session_private_key = get_session_private_key()

    session_token = get_session_token(
        user_id,
        session_id,
        client_id,
        platform_client_id,
        csdek,
        session_private_key)

    # Update user status and profile data
    session = schemas.SessionCreate(
        id=session_id,
        user_id=user_id,
        csdek=csdek,
        session_private_key=session_private_key,
        session_token=session_token,
        client_id=client_id,
        platform_client_id=platform_client_id,
    )
    crud.create_session(db=db, session=session)

    return {
        "sessionId": session_id,
        "csdek": csdek,
        "sessionToken": session_token,
        "platformClientId": platform_client_id,
    }


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
        mpesk = signup_confirmation_request.mpesk
        first_name = signup_confirmation_request.first_name
        last_name = signup_confirmation_request.last_name

        user = crud.get_user_by_email(db, email)

        if str(user.email_verification_code) != str(verification_code):  # verify email
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification code provided, please try again.",
            )

        user_id = user.id

        # Update user status and profile data
        updated_user = schemas.UserUpdate(
            first_name=first_name,
            last_name=last_name,
            status="confirmed")
        crud.update_user(db=db, db_user=user, user=updated_user)

        # Store MPESK
        crud.create_mpesk(db, mpesk=mpesk, user_id=user_id)

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Something went wrong: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Something went wrong"
        )
    else:
        # Create deafult vault
        vault = schemas.VaultCreate(name="Default Vault", is_default=True)
        crud.create_vault(db, vault, creator_id=user_id)

        # schemas.ItemCreate(
        #     title="Keylance Master Password",
        #     username=email,
        #     password=password,
        #     type="PASSWORD",
        # )
        # crud.create_item(db, item, vault_id=db_vault.id, creator_id=user_id)

        session_details = build_session(db, user_id, client_id, platform_client_id)

        # Set cookies with httpOnly flag set to true
        response.set_cookie(
            key="sessionId",
            value=session_details["sessionId"],
            httponly=True,
            max_age=7 * 24 * 60 * 60,
            secure=False,
            samesite="lax"
        )
        response.set_cookie(
            key="sessionToken",
            value=session_details["sessionToken"],
            httponly=True,
            max_age=7 * 24 * 60 * 60,
            secure=False,
            samesite="lax"
        )

        response.set_cookie(
            key="userId",
            value=user_id,
            httponly=False,
            max_age=7 * 24 * 60 * 60,
            secure=False,
            samesite="lax"
        )

        response.set_cookie(
            key="platformClientId",
            value=session_details["platformClientId"],
            httponly=True,
            max_age=7 * 24 * 60 * 60,
            secure=False,
            samesite="lax"
        )
        return {
            "csdek": session_details["csdek"]
        }


class LoginRequest(BaseModel):
    email: str
    mpesk: str


@router.post("/auth/login/", status_code=status.HTTP_200_OK, tags=["auth"])
def login(
    response: Response,
    login_request: LoginRequest,
    db: Session = Depends(get_db),
    client_id: str = Header(),
    platform_client_id: Annotated[Union[str, None], Cookie()] = None
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

        # Get user credentials
        db_mpesk = crud.get_mpesk(db, user_id)
        if db_mpesk.mpesk != mpesk:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect username or password.",
            )

        # expire active sessions
        crud.expire_active_sessions(db, user_id, client_id, platform_client_id)

        # generate session
        session_details = build_session(db, user_id, client_id, platform_client_id)

        # Set cookies with httpOnly flag set to true
        response.set_cookie(
            key="sessionId",
            value=session_details["sessionId"],
            httponly=True,
            max_age=7 * 24 * 60 * 60,
            secure=False,
            samesite="lax"
        )
        response.set_cookie(
            key="sessionToken",
            value=session_details["sessionToken"],
            httponly=True,
            max_age=7 * 24 * 60 * 60,
            secure=False,
            samesite="lax"
        )

        response.set_cookie(
            key="userId",
            value=user_id,
            httponly=False,
            max_age=7 * 24 * 60 * 60,
            secure=False,
            samesite="lax"
        )

        response.set_cookie(
            key="platformClientId",
            value=session_details["platformClientId"],
            httponly=True,
            max_age=7 * 24 * 60 * 60,
            secure=False,
            samesite="lax"
        )

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Something went wrong: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Something went wrong."
        )
    else:
        return {
            "csdek": session_details["csdek"]
        }


@router.post("/auth/logout/", status_code=status.HTTP_204_NO_CONTENT, tags=["auth"])
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
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid Session token.",
                )

            # expire active sessions which belong to specific browser/device
            crud.expire_active_sessions(
                db,
                user_id=session_details["userId"],
                client_id=session_details["clientId"],
                platform_client_id=session_details["platformClientId"]
            )

            response.delete_cookie("sessionToken")
            response.delete_cookie("sessionId")
            response.delete_cookie("userId")

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Something went wrong: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Something went wrong.",
        )


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

        # Get user credentials
        db_mpesk = crud.get_mpesk(db, user_id)
        if db_mpesk.mpesk != mpesk:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect username or password.",
            )

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
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session doesn't exists.",
            )
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Something went wrong: {e}", exc_info=True)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Something went wrong.",
        )


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
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid Session token.",
                )

            if datetime.utcnow() > db_session.expiry_at:
                # expire active sessions which belong to specific browser/device
                crud.expire_active_sessions(
                    db,
                    user_id=session_details["userId"],
                    client_id=session_details["clientId"],
                    platform_client_id=session_details["platformClientId"]
                )

                response.delete_cookie("sessionToken")
                response.delete_cookie("sessionId")
                response.delete_cookie("userId")
                return {"loggedIn": False}

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Something went wrong: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Something went wrong.",
        )
    else:
        return {"loggedIn": True}
