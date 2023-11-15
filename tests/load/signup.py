import string
import json
# import requests
import random
from secrets import choice

from .database import SessionLocal
from app.models.user import User

from srptools import SRPContext
import srptools
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

import hashlib


def get_rand_string(N=10):
    return "".join([choice(string.printable + string.digits) for _ in range(N)])


def get_verification_code(email):
    try:
        db=SessionLocal()
        verification_code = "0"
        with db.begin():
            verification_code = (
                db.query(User)
                .filter(User.email == email)
                .first()
                .__dict__["email_verification_code"]
            )
            db.close()

        return verification_code
    except Exception as e:
        db.close()
        print(f"Exception occured: {e}")
    finally:
        db.close()


def new_signup(requests, base_url, email, password):
    #### INITIATE SIGNUP PROCESS ####
    route = "/auth/signup?mock=true"

    data = {
        "email": email,
    }
    json_str = json.dumps(data)

    signup_response = requests.post(
        base_url + route,
        data=json_str,
        headers={"client-id": "b980b13c-4db8-4e8a-859c-4544fd70825f"},
    )

    #### COMPLETE SIGNUP PROCESS ####
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        #     encryption_algorithm=serialization.NoEncryption()
        encryption_algorithm=serialization.BestAvailableEncryption(
            hashed_password.encode()
        ),
    )
    context = SRPContext(email, password)
    username, password_verifier, salt = context.get_user_data_triplet()

    verification_code = get_verification_code(email)

    route = "/auth/signup/confirm"
    data = {
        "email": email,
        "verification_code": str(verification_code),
        "first_name": "qwe",
        "last_name": "qwe",
        "verifier": password_verifier,
        "salt": salt,
        "encrypted_key_wrapping_key": private_pem.decode(),
    }
    json_str = json.dumps(data)

    signup_confirmation_response = requests.post(
        base_url + route,
        data=json_str,
        headers={"client-id": "b980b13c-4db8-4e8a-859c-4544fd70825f"},
    )

    if signup_confirmation_response.status_code == 200:
        print(f"Signup complete for email: {email}")
    else:
        print(f"Signup failed for email: {email}")
