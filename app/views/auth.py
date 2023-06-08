import os
import hmac
import uuid
import random
import hashlib
import base64
import logging


import boto3
from pydantic import BaseModel
from sqlalchemy.orm import Session
from botocore.exceptions import ClientError
from fastapi import APIRouter, Depends, HTTPException, status, Header


from .. import schemas, crud
from ..database import get_db
from ..utils.security import get_session_private_key, get_session_token


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
        print(response)

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


# Endpoint for verifying email code
@router.post(
    "/auth/signup/confirm/", status_code=status.HTTP_200_OK, tags=["auth"]
)
def confirm_sign_up(
    signup_confirmation_request: SignupConfirmationRequest,
    db: Session = Depends(get_db),
    client_id: str = Header(),
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

        session_id = str(uuid.uuid4())
        csdek = str(uuid.uuid4())
        session_private_key = get_session_private_key()
        session_token = get_session_token(user_id, session_id, client_id, session_private_key)

        # Update user status and profile data
        session = schemas.SessionCreate(
            id=session_id,
            user_id=user_id,
            csdek=csdek,
            session_private_key=session_private_key,
            session_token=session_token,
            client_id=client_id
        )
        crud.create_session(db=db, session=session)

        return {
            "sessionId": session_id,
            "sessionToken": session_token,
            "userId": user_id,
            "csdek": csdek,
        }


class LoginRequest(BaseModel):
    email: str
    master_password: str


@router.post("/auth/login/", status_code=status.HTTP_200_OK, tags=["auth"])
def login(login_request: LoginRequest):
    try:
        email = login_request.email
        master_password = login_request.master_password

        login_response = cognito_client.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            ClientId=COGNITO_CLIENT_ID,
            AuthParameters={
                "USERNAME": email,
                "PASSWORD": master_password,
                "SECRET_HASH": get_secret_hash(
                    email, COGNITO_CLIENT_ID, COGNITO_CLIENT_SECRET
                ),
            },
        )

        return {
            "accessToken": login_response["AuthenticationResult"]["AccessToken"],
            "idToken": login_response["AuthenticationResult"]["IdToken"],
            "refreshToken": login_response["AuthenticationResult"]["RefreshToken"],
        }
    except ClientError as e:
        if e.response["Error"]["Code"] == "NotAuthorizedException":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect username or password.",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Something went wrong: {e}",
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Something went wrong: {e}"
        )


class LogoutRequest(BaseModel):
    access_token: str


@router.post("/auth/logout/", status_code=status.HTTP_204_NO_CONTENT, tags=["auth"])
def logout(logout_request: LogoutRequest):
    response = cognito_client.global_sign_out(AccessToken=logout_request.access_token)


class LoginRefreshRequest(BaseModel):
    refresh_token: str
    username: str


@router.post("/auth/login/refresh", status_code=status.HTTP_200_OK, tags=["auth"])
def login_refresh(login_refresh_request: LoginRefreshRequest):
    refresh_token = login_refresh_request.refresh_token
    username = login_refresh_request.username

    response = cognito_client.initiate_auth(
        ClientId="3168rpn2rk5pmb4hcgahn9pk6m",
        AuthFlow="REFRESH_TOKEN_AUTH",
        AuthParameters={
            "REFRESH_TOKEN": login_refresh_request.refresh_token,
            "SECRET_HASH": get_secret_hash(
                username, COGNITO_CLIENT_ID, COGNITO_CLIENT_SECRET
            ),
        },
    )

    return {
        "accessToken": response["AuthenticationResult"]["AccessToken"],
        "idToken": response["AuthenticationResult"]["IdToken"],
    }


@router.get("/auth/status", status_code=status.HTTP_200_OK, tags=["auth"])
async def auth_status(token: str):
    try:
        response = cognito_client.get_user(
            AccessToken=token,
        )
        return {"logged_in": True}
    except:
        return {"logged_in": False}
