import os
import hmac
import hashlib
import base64
import logging


import boto3
from pydantic import BaseModel
from sqlalchemy.orm import Session
from botocore.exceptions import ClientError
from fastapi import APIRouter, Depends, HTTPException, status


from .. import schemas, crud
from ..database import get_db


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


COGNITO_CLIENT_ID = os.environ["COGNITO_CLIENT_ID"]
COGNITO_CLIENT_SECRET = os.environ["COGNITO_CLIENT_SECRET"]
USER_POOL_ID = os.environ["USER_POOL_ID"]
cognito_client = session.client("cognito-idp", region_name=AWS_REGION_NAME)


class SignupRequest(BaseModel):  # Model for email verification request
    email: str
    first_name: str
    last_name: str
    password: str


class SignupConfirmationRequest(BaseModel):  # Model for email verification code request
    email: str
    password: str
    verification_code: str


def get_secret_hash(username, client_id, client_secret):
    message = username + client_id
    digest = hmac.new(
        str(client_secret).encode("utf-8"),
        msg=message.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).digest()
    return base64.b64encode(digest).decode()


def get_cognito_user(email):
    user_id = None
    first_name = None
    last_name = None

    get_user_response = cognito_client.admin_get_user(
        UserPoolId=USER_POOL_ID, Username=email
    )

    for attributes in get_user_response["UserAttributes"]:
        if attributes["Name"] == "sub":
            user_id = attributes["Value"]
        if attributes["Name"] == "given_name":
            first_name = attributes["Value"]
        if attributes["Name"] == "family_name":
            last_name = attributes["Value"]

    # Check the user's status
    user_status = get_user_response["UserStatus"]

    return user_id, user_status, first_name, last_name


@router.post("/auth/signup/", status_code=status.HTTP_204_NO_CONTENT, tags=["auth"])
def signup(signup_request: SignupRequest, db: Session = Depends(get_db)):
    try:
        email = signup_request.email
        first_name = signup_request.first_name
        last_name = signup_request.last_name
        secret_hash = get_secret_hash(email, COGNITO_CLIENT_ID, COGNITO_CLIENT_SECRET)
        password = signup_request.password
        user_type = None

        """
        Signup with cognito required when user is new or need_sign_up
        """

        user = crud.get_user_by_email(db, email)
        if not user:  # new user
            user_data = schemas.UserCreate(
                email=email,
                first_name=first_name,
                last_name=last_name,
                status="unconfirmed")
            user = crud.create_user(db, user_data)
            user_type = "new"
        else:
            user_type = user.status

        if user_type in ["new", "need_sign_up"]:
            cognito_client.sign_up(
                ClientId=COGNITO_CLIENT_ID,
                SecretHash=secret_hash,
                Username=email,
                Password=password,
                UserAttributes=[
                    {"Name": "email", "Value": email},
                    {"Name": "given_name", "Value": first_name},
                    {"Name": "family_name", "Value": last_name},
                    # {"Name": "custom:user_id", "Value": user.id},
                ],
            )

        elif user_type == "unconfirmed":
            cognito_client.resend_confirmation_code(
                ClientId=COGNITO_CLIENT_ID,
                SecretHash=get_secret_hash(
                    email, COGNITO_CLIENT_ID, COGNITO_CLIENT_SECRET
                ),
                Username=email,
            )

        elif user_type == "confirmed":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered.",
            )
        elif user_type == "deactivated":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email is deactivated. Please contact support for resolution.",
            )

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
    signup_confirmation_request: SignupConfirmationRequest, db: Session = Depends(get_db)
):
    try:
        email = signup_confirmation_request.email
        verification_code = signup_confirmation_request.verification_code
        password = signup_confirmation_request.password
        secret_hash = get_secret_hash(email, COGNITO_CLIENT_ID, COGNITO_CLIENT_SECRET)

        cognito_client.confirm_sign_up(
            ClientId=COGNITO_CLIENT_ID,
            SecretHash=secret_hash,
            Username=email,
            ConfirmationCode=verification_code,
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "CodeMismatchException":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification code provided, please try again.",
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
    else:
        db_user = crud.get_user_by_email(db, email)
        sub, user_status, first_name, last_name = get_cognito_user(email)
        user_id = db_user.id

        user = schemas.UserUpdate(sub=sub, status="confirmed")
        crud.update_user(db=db, db_user=db_user, user=user)

        login_response = cognito_client.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            ClientId=COGNITO_CLIENT_ID,
            AuthParameters={
                "USERNAME": email,
                "PASSWORD": password,
                "SECRET_HASH": get_secret_hash(
                    email, COGNITO_CLIENT_ID, COGNITO_CLIENT_SECRET
                ),
            },
        )
        vault = schemas.VaultCreate(name="default", is_default=True)
        db_vault = crud.create_vault(db, vault, creator_id=user_id)

        item = schemas.ItemCreate(
            title="Keylance Master Password",
            username=email,
            password=password,
            description="This is master password for your Keylance account",
            type="PASSWORD",
        )
        crud.create_item(db, item, vault_id=db_vault.id, creator_id=user_id)

        return {
            "accessToken": login_response["AuthenticationResult"]["AccessToken"],
            "idToken": login_response["AuthenticationResult"]["IdToken"],
            "refreshToken": login_response["AuthenticationResult"]["RefreshToken"],
        }


class CreatePasswordRequest(BaseModel):
    email: str
    master_password: str


# @router.post(
#     "/auth/create-password/", status_code=status.HTTP_201_CREATED, tags=["auth"]
# )
# def create_password(
#     create_password_request: CreatePasswordRequest, db: Session = Depends(get_db)
# ):
#     email = create_password_request.email
#     master_password = create_password_request.master_password

#     user_id, user_status, first_name, last_name = get_cognito_user(email)

#     crud.create_master_password(db=db, user_id=user_id, password_hash=master_password)

#     set_password_response = cognito_client.admin_set_user_password(
#         UserPoolId=USER_POOL_ID,
#         Username=email,
#         Password=master_password,
#         Permanent=True,
#     )

#     login_response = cognito_client.initiate_auth(
#         AuthFlow="USER_PASSWORD_AUTH",
#         ClientId=COGNITO_CLIENT_ID,
#         AuthParameters={
#             "USERNAME": email,
#             "PASSWORD": master_password,
#             "SECRET_HASH": get_secret_hash(
#                 email, COGNITO_CLIENT_ID, COGNITO_CLIENT_SECRET
#             ),
#         },
#     )
#     vault = schemas.VaultCreate(name="default")
#     db_vault = crud.create_vault(db, vault, creator_id=user_id)

#     item = schemas.ItemCreate(
#         title="Keylance Master Password",
#         username=email,
#         password=master_password,
#         description="This is master password for your Keylance account",
#         type="PASSWORD",
#     )
#     crud.create_item(db, item, vault_id=db_vault.id, creator_id=user_id)

#     return {
#         "accessToken": login_response["AuthenticationResult"]["AccessToken"],
#         "idToken": login_response["AuthenticationResult"]["IdToken"],
#         "refreshToken": login_response["AuthenticationResult"]["RefreshToken"],
#     }


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
