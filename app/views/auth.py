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

@router.post("/auth/signup/", status_code=status.HTTP_204_NO_CONTENT, tags=["auth"])
def signup(signup_request: SignupRequest):
    try:
        email = signup_request.email
        first_name = signup_request.first_name
        last_name = signup_request.last_name

        # define the possible characters to choose from
        alphabet = string.ascii_letters + string.digits + string.punctuation

        # generate a random password of length 12
        password = ''.join(secrets.choice(alphabet) for i in range(16))

        signup_response = cognito_client.sign_up(
            ClientId=COGNITO_CLIENT_ID,
            SecretHash=get_secret_hash(email, COGNITO_CLIENT_ID, COGNITO_CLIENT_SECRET),
            Username=email,
            Password=password,
            UserAttributes=[
                {"Name": "email", "Value": email},
                {"Name": "given_name", "Value": first_name},
                {"Name": "family_name", "Value": last_name}
            ],
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'UsernameExistsException':
            # Get the user's attributes
            get_user_response = cognito_client.admin_get_user(
                UserPoolId=USER_POOL_ID,
                Username=email
            )

            # Check the user's status
            user_status = get_user_response["UserStatus"]

            if user_status == 'UNCONFIRMED':
               send_code_response = cognito_client.resend_confirmation_code(
                    ClientId=COGNITO_CLIENT_ID,
                    SecretHash=get_secret_hash(email, COGNITO_CLIENT_ID, COGNITO_CLIENT_SECRET),
                    Username=email
                )
            elif user_status == 'CONFIRMED':
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered.")
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Something went wrong. Please try again.")

# Endpoint for verifying email code
@router.post("/auth/email-verification/", status_code=status.HTTP_204_NO_CONTENT, tags=["auth"])
def verify_email_code(email_verification_request: EmailVerificationRequest):
    try:
        response = cognito_client.confirm_sign_up(
            ClientId=COGNITO_CLIENT_ID,
            SecretHash=get_secret_hash(email_verification_request.email, COGNITO_CLIENT_ID, COGNITO_CLIENT_SECRET),
            Username=email_verification_request.email,
            ConfirmationCode=email_verification_request.verification_code,
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Something went wrong: {e}")


class CreatePasswordRequest(BaseModel):
    email: str
    master_password: str


@router.post("/auth/create-password/", status_code=status.HTTP_201_CREATED, tags=["auth"])
def create_password(create_password_request: CreatePasswordRequest, db: Session = Depends(get_db)):

    email = create_password_request.email
    master_password = create_password_request.master_password

    get_user_response = cognito_client.admin_get_user(
        UserPoolId=USER_POOL_ID,
        Username=email
    )

    user_id = None

    for attributes in get_user_response["UserAttributes"]:
        if attributes["Name"] == "sub":
            user_id = attributes["Value"]

    # crud.create_master_password(
    #     db=db,
    #     user_id=user_id,
    #     password_hash=master_password)


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

    return {
        "accessToken": login_response["AuthenticationResult"]["AccessToken"],
        "idToken": login_response["AuthenticationResult"]["RefreshToken"],
    }


