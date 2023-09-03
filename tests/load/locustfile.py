import os
import time
import json
import random
from secrets import choice
import string
import base64
import uuid

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from locust import HttpUser, task, between, TaskSet

from signup import new_signup
from login import complete_login


def get_rand_string(N=10):
    return "".join([choice(string.ascii_letters + string.digits) for _ in range(N)])


def encrypt_data(data):
    key = os.urandom(32)
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv))
    encryptor = cipher.encryptor()
    ct = encryptor.update(data.encode()) + encryptor.finalize()
    ct_base64 = base64.b64encode(ct).decode() + base64.b64encode(iv).decode()
    return ct_base64


def get_rand_item_data():
    return {
        "title": encrypt_data(get_rand_string(10)),
        "description": encrypt_data(get_rand_string(20)),
        "username": encrypt_data(get_rand_string(10)),
        "password": encrypt_data(get_rand_string(10)),
        "website": encrypt_data(get_rand_string(10)) + ".com",
        "notes": encrypt_data(get_rand_string(5)),
        "type": "PASSWORD",
        "encryptedEncryptionKey": encrypt_data(str(uuid.uuid4())),
    }


class NormalUser(HttpUser):
    # host = "http://0.0.0.0:8000/api/v1"
    host = "https://dev.api.terafill.com/api/v1"
    wait_time = between(0.5, 5)
    login_data = {}
    cookies = {}
    email = ""
    password = ""

    @task
    def hello_world(self):
        self.client.get("/hello")

    @task
    def login_status(self):
        response = self.client.get("/auth/status", cookies=self.cookies)

    @task
    class LoggedInUser(TaskSet):
        vault_list = []
        vault_items = {}

        @task(1)
        def read_vaults(self):
            response = self.client.get("/users/me/vaults", cookies=self.user.cookies)
            self.vault_list = response.json()
            self.read_items()

        @task(1)
        def read_items(self):
            for vault in self.vault_list:
                response = self.client.get(
                    f"/users/me/vaults/{vault['id']}/items",
                    cookies=self.user.cookies,
                    name="/users/me/vaults/{vault_id}/items",
                )
                self.vault_items[vault["id"]] = response.json()

        @task(2)
        def create_vault(self):
            data = {
                "name": f"test {get_rand_string(10)}",
                "description": f"this is a test vault {get_rand_string(10)}",
            }
            json_str = json.dumps(data)
            response = self.client.post(
                "/users/me/vaults",
                cookies=self.user.cookies,
                data=json_str,
                name="/users/me/vaults",
            )
            # print("create vault", response.status_code)
            self.read_vaults()

        @task(8)
        def update_vault(self):
            if self.vault_list:
                import random

                vault = random.choice(self.vault_list)
                data = {
                    "name": f"test {get_rand_string(10)}",
                    "description": f"this is a test vault {get_rand_string(10)}",
                }
                json_str = json.dumps(data)
                response = self.client.put(
                    f"/users/me/vaults/{vault['id']}",
                    cookies=self.user.cookies,
                    data=json_str,
                    name="/users/me/vaults/{vault_id}",
                )
                # print("update vault", response.status_code)
                self.read_vaults()

        @task(1)
        def delete_vault(self):
            if self.vault_list:
                import random

                vault = random.choice(self.vault_list)
                response = self.client.delete(
                    f"/users/me/vaults/{vault['id']}",
                    cookies=self.user.cookies,
                    name="/users/me/vaults/{vault_id}",
                )
                self.read_vaults()
                # print("delete vault", response.status_code)

        @task(20)
        def create_item(self):
            if self.vault_list:
                vault = random.choice(self.vault_list)

                data = get_rand_item_data()
                json_str = json.dumps(data)
                response = self.client.post(
                    f"/users/me/vaults/{vault['id']}/items",
                    cookies=self.user.cookies,
                    data=json_str,
                    name="/users/me/vaults/{vault_id}/items",
                )
                # print("create vault item", response.status_code)
                self.read_items()

        @task(16)
        def update_item(self):
            if self.vault_list:
                vault = random.choice(self.vault_list)
                if self.vault_items[vault["id"]]:
                    item = random.choice(self.vault_items[vault["id"]])
                    data = get_rand_item_data()
                    json_str = json.dumps(data)
                    response = self.client.put(
                        f"/users/me/vaults/{vault['id']}/items/{item['id']}",
                        cookies=self.user.cookies,
                        data=json_str,
                        name="/users/me/vaults/{vault_id}/items/{item_id}",
                    )
                    # print("update vault item", response.status_code)
                    self.read_items()

        @task(1)
        def delete_item(self):
            if self.vault_list:
                vault = random.choice(self.vault_list)
                if self.vault_items[vault["id"]]:
                    item = random.choice(self.vault_items[vault["id"]])
                    response = self.client.delete(
                        f"/users/me/vaults/{vault['id']}/items/{item['id']}",
                        cookies=self.user.cookies,
                        name="/users/me/vaults/{vault_id}/items/{item_id}",
                    )
                    self.read_items()
                    # print("delete vault item", response.status_code)

    def on_start(self):
        self.email = f"{get_rand_string(8)}@keylance.io"
        self.password = get_rand_string(10)

        new_signup(
            requests=self.client,
            base_url=self.host,
            email=self.email,
            password=self.password,
        )

        self.login_data = complete_login(
            requests=self.client,
            email=self.email,
            password=self.password,
            base_url=self.host,
        )

        self.cookies = {
            "sessionToken": self.login_data["session_token"],
            "userId": self.login_data["user_id"],
            "sessionId": self.login_data["session_id"],
        }

    def on_stop(self):
        from database import SessionLocal, User
        from app.models.encryption_key import EncryptionKey
        from app.models.item import Item
        from app.models.session import Session
        from app.models.srp_data import SRPData
        from app.models.key_wrapping_key import KeyWrappingKey
        from app.models.vault import Vault

        db = SessionLocal()

        with db.begin():
            try:
                user = db.query(User).filter(User.email == self.email).first()
                if user:
                    user_id = user.id
                    db.query(Item).filter(Item.creator_id == user_id).delete()
                    db.query(Vault).filter(Vault.creator_id == user_id).delete()
                    db.query(EncryptionKey).filter(
                        EncryptionKey.user_id == user_id
                    ).delete()
                    db.query(KeyWrappingKey).filter(
                        KeyWrappingKey.user_id == user_id
                    ).delete()
                    db.query(SRPData).filter(SRPData.user_id == user_id).delete()
                    db.query(Session).filter(Session.user_id == user_id).delete()

                    response = db.delete(user)
                    print(f"User {self.email} deleted successfully.", response)
                    db.commit()
                else:
                    print("User not found")
            except Exception as e:
                db.close()
                raise
            finally:
                db.close()
