import json
import jwt

import pytest
from werkzeug.security import check_password_hash


def test_register_new_user(client):
    response = client.post(
        "/auth/register",
        json={"username": "uname", "password": "pword", "email": "email@addr.com"},
    )
    assert response.status == "201 CREATED"


def test_register_duplicate_users_response(client):
    user_json = {"username": "uname", "password": "pword", "email": "email@addr.com"}
    client.post("/auth/register", json=user_json)
    response = client.post("/auth/register", json=user_json)

    assert response.status == "409 CONFLICT"


def test_register_duplicate_users_text(client):
    user_json = {"username": "uname", "password": "pword", "email": "email@addr.com"}
    client.post("/auth/register", json=user_json)
    response = client.post("/auth/register", json=user_json)

    assert response.text == "Issue registering"


def test_register_user_empty_json(client):
    user_json = {}
    response = client.post("/auth/register", json=user_json)
    assert response.status == "400 BAD REQUEST"


def test_register_user_no_json(client):
    response = client.post("/auth/register")
    assert response.status == "415 UNSUPPORTED MEDIA TYPE"


def test_register_no_username(client):
    user_json = {"password": "pword", "email": "email@addr.com"}
    client.post("/auth/register", json=user_json)
    response = client.post("/auth/register", json=user_json)

    assert response.status == "400 BAD REQUEST"


def test_register_no_password(client):
    user_json = {"username": "uname", "email": "email@addr.com"}
    client.post("/auth/register", json=user_json)
    response = client.post("/auth/register", json=user_json)

    assert response.status == "400 BAD REQUEST"


def test_register_no_email(client):
    user_json = {
        "username": "uname",
        "password": "pword",
    }
    client.post("/auth/register", json=user_json)
    response = client.post("/auth/register", json=user_json)

    assert response.status == "400 BAD REQUEST"


@pytest.mark.parametrize(
    "test_input", [None, "", "a.b.c", "a@b", "@gmail.com", "www.a@com"]
)
def test_register_invalid_emails(client, test_input):
    user_json = {"username": "uname", "password": "pword", "email": test_input}
    client.post("/auth/register", json=user_json)
    response = client.post("/auth/register", json=user_json)

    assert response.status == "400 BAD REQUEST"


@pytest.mark.parametrize("test_input", [None, ""])
def test_register_invalid_usernames(client, test_input):
    user_json = {"username": test_input, "password": "pword", "email": "test@email.com"}
    client.post("/auth/register", json=user_json)
    response = client.post("/auth/register", json=user_json)

    assert response.status == "400 BAD REQUEST"


@pytest.mark.parametrize("test_input", [None, ""])
def test_register_invalid_password(client, test_input):
    user_json = {"username": "uname", "password": test_input, "email": "test@email.com"}
    client.post("/auth/register", json=user_json)
    response = client.post("/auth/register", json=user_json)

    assert response.status == "400 BAD REQUEST"


def test_register_valid_login_status(client):
    user_json = {"username": "uname", "password": "pword", "email": "test@email.com"}
    client.post("/auth/register", json=user_json)
    response = client.post("/auth/register", json=user_json)

    user_json = {
        "username": "uname",
        "password": "pword",
    }
    client.post("/auth/register", json=user_json)
    response = client.post("/auth/login", json=user_json)

    assert response.status == "200 OK"


def test_register_invalid_login_status(client):
    user_json = {"username": "uname", "password": "pword", "email": "test@email.com"}
    client.post("/auth/register", json=user_json)
    response = client.post("/auth/register", json=user_json)

    user_json = {
        "username": "uname",
        "password": "wrongpword",
    }
    client.post("/auth/register", json=user_json)
    response = client.post("/auth/login", json=user_json)

    assert response.status == "401 UNAUTHORIZED"


# def test_register_invalid_login_status(client):
#     user_json = {"username": "uname", "password": "pword", "email": "test@email.com"}
#     client.post("/auth/register", json=user_json)
#     response = client.post("/auth/register", json=user_json)
#
#     user_json = {
#         "username": "uname",
#         "password": "wrongpword",
#     }
#     client.post("/auth/register", json=user_json)
#     response = client.post("/auth/login", json=user_json)
#
#     assert response.status == "401 UNAUTHORIZED"


def test_password_is_hashed(client, fake_crossword_user_databases):
    user_json = {"username": "uname", "password": "pword", "email": "test@email.com"}
    client.post("/auth/register", json=user_json)
    user_id = fake_crossword_user_databases.get_id_for_username("uname")
    user_data = fake_crossword_user_databases.get_user_data(user_id["Item"]["id"])
    assert user_data["Item"]["password"] != "pword"
    assert check_password_hash(user_data["Item"]["password"], "pword")


def test_valid_login_message(client):
    user_json = {"username": "uname", "password": "pword", "email": "test@email.com"}
    client.post("/auth/register", json=user_json)
    client.post("/auth/register", json=user_json)

    user_json = {
        "username": "uname",
        "password": "pword",
    }
    client.post("/auth/register", json=user_json)
    response = client.post("/auth/login", json=user_json)

    resp_data = json.loads(response.text)

    decoded = jwt.decode(resp_data["token"], "iLoveCats", algorithms=["HS256"])

    assert decoded
