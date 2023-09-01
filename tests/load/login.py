import json

# import requests
from srptools import SRPContext, SRPClientSession


def complete_login(requests, email, password, base_url):
    route = "/auth/salt"
    data = {"email": email}
    json_str = json.dumps(data)
    response = requests.post(
        base_url + route,
        data=json_str,
        headers={"client-id": "b980b13c-4db8-4e8a-859c-4544fd70825f"},
    )

    salt = response.json()["salt"]

    # Receive server public and salt and process them.
    client_session = SRPClientSession(SRPContext(email, password))

    # Generate client public and session key.
    client_public = client_session.public

    route = "/auth/login"
    data = {"email": email, "clientPublicKey": client_public}
    json_str = json.dumps(data)
    login_response = requests.post(
        base_url + route,
        data=json_str,
        headers={"client-id": "b980b13c-4db8-4e8a-859c-4544fd70825f"},
    )

    # print(
    #     login_response.cookies.get("platformClientId"),
    #     login_response.cookies.get("userId"),
    #     login_response.cookies.get("sessionId")
    # , sep="\n")

    login_response.json()

    login_response.raw.getheaders()

    server_public = login_response.json()["serverPublicKey"]
    server_public

    client_session.process(server_public, salt=salt)

    client_session_key_proof = client_session.key_proof
    client_session_key_proof

    route = "/auth/login/confirm"
    data = {
        "email": email,
        "clientProof": client_session_key_proof.decode(),
    }
    json_str = json.dumps(data)
    login_confirm_response = requests.post(
        base_url + route,
        data=json_str,
        headers={"client-id": "b980b13c-4db8-4e8a-859c-4544fd70825f"},
        cookies={
            "platformClientId": login_response.cookies.get("platformClientId"),
            "sessionId": login_response.cookies.get("sessionId"),
        },
    )

    login_confirm_response.json()

    server_session_key_proof_hash = login_confirm_response.json()["serverProof"]
    server_session_key_proof_hash

    # Verify session key proof hash received from server.
    client_session.verify_proof(server_session_key_proof_hash.encode())

    platform_client_id = login_response.cookies.get("platformClientId")
    session_id = login_response.cookies.get("sessionId")
    user_id = login_response.cookies.get("userId")
    session_token = login_confirm_response.cookies.get("sessionToken")

    return {
        "platform_client_id": platform_client_id,
        "session_id": session_id,
        "user_id": user_id,
        "session_token": session_token,
    }


# base_url = "http://0.0.0.0:8000/api/v1"
# email = "harshitsaini15@gmail.com"
# password = "test"

# complete_login(email=email, password=password, base_url=base_url)
