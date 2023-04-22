import os
import hmac
import hashlib
import base64
import string
import secrets
import random
from typing import List, Optional


import boto3
import redis
from jose import jwt
from pydantic import BaseModel
from sqlalchemy.orm import Session
from botocore.exceptions import ClientError
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException, status


from .. import models, schemas, crud
from ..database import get_db
from ..utils.security import get_current_user, get_token, security_scheme


router = APIRouter()
# redis_client = redis.Redis(decode_responses=True)

# Set up AWS credentials
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_REGION_NAME = os.environ['AWS_REGION_NAME']


# Create a new session
session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION_NAME
)


COGNITO_CLIENT_ID = os.environ["COGNITO_CLIENT_ID"]
COGNITO_CLIENT_SECRET = os.environ["COGNITO_CLIENT_SECRET"]
USER_POOL_ID = os.environ["USER_POOL_ID"]
cognito_client = session.client('cognito-idp', region_name=AWS_REGION_NAME)

# ses_client = session.client('ses', region_name=AWS_REGION_NAME)  # Replace with your desired region

# Model for email verification request
class SignupRequest(BaseModel):
    email: str
    first_name: str
    last_name: str


# Model for email verification code request
class EmailVerificationRequest(BaseModel):
    email: str
    verification_code: str


def get_secret_hash(username, client_id, client_secret):
    message = username + client_id
    digest = hmac.new(str(client_secret).encode('utf-8'), msg=message.encode('utf-8'), digestmod=hashlib.sha256).digest()
    return base64.b64encode(digest).decode()


def get_random_password():
    # define the possible characters to choose from
    alphabet = string.ascii_letters + string.digits + string.punctuation

    # generate a random password of length 12
    password = ''.join(secrets.choice(alphabet) for i in range(16))

    return password


def get_cognito_user(email):
    user_id = None
    first_name = None
    last_name = None

    get_user_response = cognito_client.admin_get_user(
        UserPoolId=USER_POOL_ID,
        Username=email
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
        password = get_random_password()
        user_id = None
        user_status = None

        signup_response = cognito_client.sign_up(
            ClientId=COGNITO_CLIENT_ID,
            SecretHash=secret_hash,
            Username=email,
            Password=password,
            UserAttributes=[
                {"Name": "email", "Value": email},
                {"Name": "given_name", "Value": first_name},
                {"Name": "family_name", "Value": last_name}
            ],
        )

        user_id, user_status, first_name, last_name = get_cognito_user(email)

    except ClientError as e:
        if e.response['Error']['Code'] == 'UsernameExistsException':
            if not user_status:
                user_id, user_status, first_name, last_name = get_cognito_user(email)
            if user_status == 'UNCONFIRMED':
               send_code_response = cognito_client.resend_confirmation_code(
                    ClientId=COGNITO_CLIENT_ID,
                    SecretHash=get_secret_hash(email, COGNITO_CLIENT_ID, COGNITO_CLIENT_SECRET),
                    Username=email
                )

            elif user_status == 'CONFIRMED':
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered.")
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Something went wrong. Please try again.")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Something went wrong. Please try again.")


# Endpoint for verifying email code
@router.post("/auth/email-verification/", status_code=status.HTTP_204_NO_CONTENT, tags=["auth"])
def verify_email_code(email_verification_request: EmailVerificationRequest, db: Session = Depends(get_db)):
    try:
        email = email_verification_request.email
        verification_code = email_verification_request.verification_code
        secret_hash = get_secret_hash(email, COGNITO_CLIENT_ID, COGNITO_CLIENT_SECRET)

        response = cognito_client.confirm_sign_up(
            ClientId=COGNITO_CLIENT_ID,
            SecretHash=secret_hash,
            Username=email,
            ConfirmationCode=verification_code,
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'CodeMismatchException':
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification code provided, please try again.")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Something went wrong: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Something went wrong: {e}")
    else:
        user_id = None
        db_user = crud.get_user_by_email(db, email=email)
        if not db_user:
            if not user_id:
                user_id, user_status, first_name, last_name = get_cognito_user(email)


            user = schemas.UserCreate(
                id=user_id,
                email=email,
                first_name=first_name,
                last_name=last_name)
            crud.create_user(db=db, user=user)


class CreatePasswordRequest(BaseModel):
    email: str
    master_password: str


@router.post("/auth/create-password/", status_code=status.HTTP_201_CREATED, tags=["auth"])
def create_password(create_password_request: CreatePasswordRequest, db: Session = Depends(get_db)):

    email = create_password_request.email
    master_password = create_password_request.master_password

    user_id, user_status, first_name, last_name = get_cognito_user(email)

    crud.create_master_password(
        db=db,
        user_id=user_id,
        password_hash=master_password)


    set_password_response = cognito_client.admin_set_user_password(
        UserPoolId=USER_POOL_ID,
        Username=email,
        Password=master_password,
        Permanent=True
    )

    login_response = cognito_client.initiate_auth(
        AuthFlow="USER_PASSWORD_AUTH",
        ClientId=COGNITO_CLIENT_ID,
        AuthParameters={
            "USERNAME": email,
            "PASSWORD": master_password,
            "SECRET_HASH": get_secret_hash(email, COGNITO_CLIENT_ID, COGNITO_CLIENT_SECRET)
        }
    )
    vault = schemas.VaultCreate(
        name="default"
        )
    db_vault = crud.create_vault(db, vault, creator_id=user_id)

    item  = schemas.ItemCreate(
        title="Keylance Master Password",
        username=email,
        password=master_password,
        description="This is master password for your Keylance account",
        type="PASSWORD"
        )
    crud.create_item(db, item, vault_id=db_vault.id, creator_id=user_id)

    return {
        "accessToken": login_response["AuthenticationResult"]["AccessToken"],
        "idToken": login_response["AuthenticationResult"]["IdToken"],
        "refreshToken": login_response["AuthenticationResult"]["RefreshToken"]
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
                "SECRET_HASH": get_secret_hash(email, COGNITO_CLIENT_ID, COGNITO_CLIENT_SECRET)
            }
        )

        return {
            "accessToken": login_response["AuthenticationResult"]["AccessToken"],
            "idToken": login_response["AuthenticationResult"]["IdToken"],
            "refreshToken": login_response["AuthenticationResult"]["RefreshToken"]
        }
    except ClientError as e:
        if e.response['Error']['Code'] == 'NotAuthorizedException':
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password.")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Something went wrong: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Something went wrong: {e}")

class LogoutRequest(BaseModel):
    access_token: str


@router.post("/auth/logout/", status_code=status.HTTP_204_NO_CONTENT, tags=["auth"])
def logout(logout_request: LogoutRequest):

    response = cognito_client.global_sign_out(
       AccessToken=logout_request.access_token
    )


class LoginRefreshRequest(BaseModel):
    refresh_token: str
    username: str



@router.post("/auth/login/refresh", status_code=status.HTTP_200_OK, tags=["auth"])
def login_refresh(login_refresh_request: LoginRefreshRequest):

    refresh_token = login_refresh_request.refresh_token
    username = login_refresh_request.username

    response = cognito_client.initiate_auth(
        ClientId="3168rpn2rk5pmb4hcgahn9pk6m",
        AuthFlow='REFRESH_TOKEN_AUTH',
        AuthParameters={
            'REFRESH_TOKEN': login_refresh_request.refresh_token,
            "SECRET_HASH": get_secret_hash(username, COGNITO_CLIENT_ID, COGNITO_CLIENT_SECRET)
        }
    )

    return {
        "accessToken": response["AuthenticationResult"]["AccessToken"],
        "idToken": response["AuthenticationResult"]["IdToken"],
    }


@router.get('/auth/status', status_code=status.HTTP_200_OK, tags=["auth"])
async def auth_status(token: str):
    try:
        response = cognito_client.get_user(
            AccessToken=token,
        )
        return {'logged_in': True}
    except:
        return {'logged_in': False}
