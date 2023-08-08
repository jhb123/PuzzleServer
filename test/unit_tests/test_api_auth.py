import json
import jwt

import pytest
from werkzeug.security import check_password_hash

from flaskr.auth import verify_token


def test_register_new_user(flask_client, new_user):
    response = flask_client.post(
        "/auth/register",
        json=new_user,
    )
    assert response.status == "201 CREATED"


def test_register_duplicate_users_response(flask_client, new_user):
    flask_client.post("/auth/register", json=new_user)
    response = flask_client.post("/auth/register", json=new_user)

    assert response.status == "409 CONFLICT"


def test_register_duplicate_users_text(flask_client, new_user):
    flask_client.post("/auth/register", json=new_user)
    response = flask_client.post("/auth/register", json=new_user)

    assert response.text == "Issue registering"


def test_register_user_empty_json(flask_client):
    user_json = {}
    response = flask_client.post("/auth/register", json=user_json)
    assert response.status == "400 BAD REQUEST"


def test_register_user_no_json(flask_client):
    response = flask_client.post("/auth/register")
    assert response.status == "415 UNSUPPORTED MEDIA TYPE"


def test_register_no_username(flask_client):
    user_json = {"password": "pword", "email": "email@addr.com"}
    flask_client.post("/auth/register", json=user_json)
    response = flask_client.post("/auth/register", json=user_json)

    assert response.status == "400 BAD REQUEST"


def test_register_no_password(flask_client):
    user_json = {"username": "uname", "email": "email@addr.com"}
    flask_client.post("/auth/register", json=user_json)
    response = flask_client.post("/auth/register", json=user_json)

    assert response.status == "400 BAD REQUEST"


def test_register_no_email(flask_client):
    user_json = {
        "username": "uname",
        "password": "pword",
    }
    flask_client.post("/auth/register", json=user_json)
    response = flask_client.post("/auth/register", json=user_json)

    assert response.status == "400 BAD REQUEST"


@pytest.mark.parametrize(
    "test_input", [None, "", "a.b.c", "a@b", "@gmail.com", "www.a@com"]
)
def test_register_invalid_emails(flask_client, test_input):
    user_json = {"username": "uname", "password": "pword", "email": test_input}
    flask_client.post("/auth/register", json=user_json)
    response = flask_client.post("/auth/register", json=user_json)

    assert response.status == "400 BAD REQUEST"


@pytest.mark.parametrize("test_input", [None, ""])
def test_register_invalid_usernames(flask_client, test_input):
    user_json = {"username": test_input, "password": "pword", "email": "test@email.com"}
    flask_client.post("/auth/register", json=user_json)
    response = flask_client.post("/auth/register", json=user_json)

    assert response.status == "400 BAD REQUEST"


@pytest.mark.parametrize("test_input", [None, ""])
def test_register_invalid_password(flask_client, test_input):
    user_json = {"username": "uname", "password": test_input, "email": "test@email.com"}
    flask_client.post("/auth/register", json=user_json)
    response = flask_client.post("/auth/register", json=user_json)

    assert response.status == "400 BAD REQUEST"


def test_register_valid_login_status(flask_client):
    user_json = {"username": "uname", "password": "pword", "email": "test@email.com"}
    flask_client.post("/auth/register", json=user_json)

    user_json = {
        "username": "uname",
        "password": "pword",
    }
    flask_client.post("/auth/register", json=user_json)
    response = flask_client.post("/auth/login", json=user_json)

    assert response.status == "200 OK"


def test_register_invalid_login_status(flask_client):
    user_json = {"username": "uname", "password": "pword", "email": "test@email.com"}
    flask_client.post("/auth/register", json=user_json)

    user_json = {
        "username": "uname",
        "password": "wrongpword",
    }
    flask_client.post("/auth/register", json=user_json)
    response = flask_client.post("/auth/login", json=user_json)

    assert response.status == "401 UNAUTHORIZED"


def test_password_is_hashed(flask_client, fake_crossword_user_databases, new_user):
    flask_client.post("/auth/register", json=new_user)
    user_id = fake_crossword_user_databases.get_id_for_username("uname")
    user_data = fake_crossword_user_databases.get_user_data(user_id["Item"]["id"])
    assert user_data["Item"]["password"] != "pword"
    assert check_password_hash(user_data["Item"]["password"], "pword")


def test_valid_login_message(flask_client, new_user):
    flask_client.post("/auth/register", json=new_user)

    user_json = {
        "username": "uname",
        "password": "pword",
    }
    response = flask_client.post("/auth/login", json=user_json)

    resp_data = json.loads(response.text)

    decoded = jwt.decode(resp_data["token"], "iLoveCats", algorithms=["HS256"])

    assert decoded


def test_verify_repeat_login(flask_client, new_user):
    # user_json = {"username": "uname", "password": "pword", "email": "test@email.com"}
    response = flask_client.post("/auth/register", json=new_user)
    token_1 = json.loads(response.text)["token"]
    response = flask_client.post("/auth/login", json=new_user)
    token_2 = json.loads(response.text)["token"]
    assert token_1 == token_2


def test_verify_token(app, flask_client, new_user):
    response = flask_client.post("/auth/register", json=new_user)
    token = json.loads(response.text)["token"]
    with app.app_context():
        assert verify_token(token)


def test_verify_bad_token(app, flask_client):
    with app.app_context():
        assert not verify_token("1")


def test_get_reset_password_status_happy_path(flask_client, new_user, delete_emails):
    flask_client.post("/auth/register", json=new_user)
    response = flask_client.get(
        "/auth/resetPassword", query_string={"email": "email@addr.com"}
    )
    assert response.status == "200 OK"


def test_get_reset_password_email_received(
    flask_client, messages, fake_crossword_user_databases, new_user, delete_emails
):
    flask_client.post("/auth/register", json=new_user)
    flask_client.get("/auth/resetPassword", query_string={"email": "email@addr.com"})
    user_id = fake_crossword_user_databases.get_id_for_username("uname")
    user_data = fake_crossword_user_databases.get_user_data(user_id["Item"]["id"])
    assert user_data["Item"]["resetGuid"] in messages[0].body


@pytest.mark.parametrize(
    "test_input", [None, "", "a.b.c", "a@b", "@gmail.com", "www.a@com"]
)
def test_get_reset_password_bad_email(flask_client, test_input):
    user_json = {"username": "uname", "password": "pword", "email": test_input}
    flask_client.post("/auth/register", json=user_json)
    response = flask_client.get(
        "/auth/resetPassword", query_string={"email": test_input}
    )

    assert response.status == "400 BAD REQUEST"


@pytest.mark.parametrize(
    "test_input", [None, "", "a.b.c", "a@b", "@gmail.com", "www.a@com"]
)
def test_get_reset_password_bad_email_no_email_sent(
    flask_client, messages, test_input, delete_emails
):
    # check no emails are sent when a bad email is used
    user_json = {"username": "uname", "password": "pword", "email": test_input}
    flask_client.post("/auth/register", json=user_json)
    flask_client.get("/auth/resetPassword", query_string={"email": test_input})
    assert len(messages) == 0


def test_post_reset_password_status(flask_client, fake_crossword_user_databases):
    old_password = "old_password"
    new_password = "new_password"

    user_json = {
        "username": "uname",
        "password": old_password,
        "email": "test@email.com",
    }
    flask_client.post("/auth/register", json=user_json)

    user_id = fake_crossword_user_databases.get_id_for_username("uname")
    user_data = fake_crossword_user_databases.get_user_data(user_id["Item"]["id"])
    old_reset_code = user_data["Item"]["resetGuid"]

    response = flask_client.get(
        "/auth/resetPassword", query_string={"email": "test@email.com"}
    )
    flask_client.post(
        "/auth/resetPassword",
        json={
            "username": "uname",
            "password": new_password,
            "resetGuid": old_reset_code,
        },
    )

    assert response.status == "200 OK"


def test_post_reset_password_status_new_code(
    flask_client, fake_crossword_user_databases
):
    old_password = "old_password"
    new_password = "new_password"

    user_json = {
        "username": "uname",
        "password": old_password,
        "email": "test@email.com",
    }
    flask_client.post("/auth/register", json=user_json)

    user_id = fake_crossword_user_databases.get_id_for_username("uname")
    user_data = fake_crossword_user_databases.get_user_data(user_id["Item"]["id"])
    old_reset_code = user_data["Item"]["resetGuid"]

    # flask_client.get("/auth/resetPassword", query_string={"email": "test@email.com"})
    flask_client.post(
        "/auth/resetPassword",
        json={
            "username": "uname",
            "password": new_password,
            "resetGuid": old_reset_code,
        },
    )

    user_data = fake_crossword_user_databases.get_user_data(user_id["Item"]["id"])
    new_reset_code = user_data["Item"]["resetGuid"]

    assert old_reset_code != new_reset_code


def test_post_reset_password_status_new_password(
    flask_client, fake_crossword_user_databases, new_user
):
    expected_new_password = "new_password"
    flask_client.post("/auth/register", json=new_user)

    user_id = fake_crossword_user_databases.get_id_for_username("uname")
    user_data = fake_crossword_user_databases.get_user_data(user_id["Item"]["id"])
    old_reset_code = user_data["Item"]["resetGuid"]

    # flask_client.get("/auth/resetPassword", query_string={"email": "test@email.com"})
    flask_client.post(
        "/auth/resetPassword",
        json={
            "username": "uname",
            "password": expected_new_password,
            "resetGuid": old_reset_code,
        },
    )

    user_data = fake_crossword_user_databases.get_user_data(user_id["Item"]["id"])
    hashed_actual_new_password = user_data["Item"]["password"]

    assert check_password_hash(hashed_actual_new_password, expected_new_password)


@pytest.mark.parametrize("test_input", [None, "", "test@email.com"])
def test_post_reset_password_invalid_username(
    flask_client, fake_crossword_user_databases, test_input, new_user
):
    flask_client.post("/auth/register", json=new_user)

    user_id = fake_crossword_user_databases.get_id_for_username("uname")
    user_data = fake_crossword_user_databases.get_user_data(user_id["Item"]["id"])
    old_reset_code = user_data["Item"]["resetGuid"]

    response = flask_client.post(
        "/auth/resetPassword",
        json={
            "username": test_input,
            "password": "password2",
            "resetGuid": old_reset_code,
        },
    )

    assert response.status == "400 BAD REQUEST"


@pytest.mark.parametrize("test_input", [None, ""])
def test_post_reset_password_invalid_new_password(
    flask_client, fake_crossword_user_databases, test_input, new_user
):
    flask_client.post("/auth/register", json=new_user)

    user_id = fake_crossword_user_databases.get_id_for_username("uname")
    user_data = fake_crossword_user_databases.get_user_data(user_id["Item"]["id"])
    old_reset_code = user_data["Item"]["resetGuid"]

    response = flask_client.post(
        "/auth/resetPassword",
        json={"username": "uname", "password": test_input, "resetGuid": old_reset_code},
    )

    assert response.status == "400 BAD REQUEST"


@pytest.mark.parametrize("test_input", [None, "", "not a valid reset code"])
def test_post_reset_invalid_reset_code(
    flask_client, fake_crossword_user_databases, test_input, new_user
):
    flask_client.post("/auth/register", json=new_user)

    response = flask_client.post(
        "/auth/resetPassword",
        json={"username": "uname", "password": "password2", "resetGuid": test_input},
    )

    assert response.status == "400 BAD REQUEST"
