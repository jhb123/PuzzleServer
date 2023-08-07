import uuid
from functools import wraps

import jwt
from flask import (
    Blueprint,
    redirect,
    request,
    session,
    url_for,
    current_app,
    jsonify,
)
from pyisemail import is_email
from werkzeug.security import check_password_hash, generate_password_hash

bp = Blueprint("auth", __name__, url_prefix="/auth")

# Secret key used to sign and verify the JWTs
# secret_key = 'iLoveCats'


@bp.route("/register", methods=["POST"])
def register():
    current_app.logger.info("Beginning registration")
    username = request.json.get("username")
    password = request.json.get("password")
    email = request.json.get("email")

    error = None

    valid_email = False

    try:
        valid_email = is_email(email, check_dns=True)
        current_app.logger.info("Email input fit expected regex rules")
    except TypeError:
        error = "Email was not a string"

    if not username:
        error = "Username is required."
    elif not password:
        error = "Password is required."
    elif not valid_email:
        error = "Email is not valid."

    if error is not None:
        current_app.logger.info(error)
        return error, 400

    current_app.logger.info("generating user id")
    user_id = str(uuid.uuid4())
    current_app.logger.info("hashing password")
    hashed_password = generate_password_hash(password)
    current_app.logger.info("generating reset code")
    reset_code = str(uuid.uuid4())

    success = current_app.user_database.register_new_user(
        user_id, username, hashed_password, email, reset_code
    )
    if success:
        token = generate_token(username)
        return jsonify({"token": token}), 201
    else:  # figure out how to tell if its username or email which is conflicted.
        error = "Issue registering"
        return error, 409


# Generate a token for a given user
def generate_token(username):
    token = jwt.encode(
        {"username": username}, current_app.config["JWT_KEY"], algorithm="HS256"
    )
    return token


# Verify and decode a token
def verify_token(token):
    try:
        decoded = jwt.decode(token, current_app.config["JWT_KEY"], algorithms=["HS256"])
        return decoded
    except jwt.InvalidTokenError:
        return None


# Route for user login
@bp.route("/login", methods=["POST"])
def login():
    # Authenticate the user (e.g., check username and password)
    # If authentication is successful, generate a token
    username = request.json.get("username")
    password = request.json.get("password")

    response = current_app.user_database.get_id_for_username(username)
    status_code = response["ResponseMetadata"]["HTTPStatusCode"]
    if status_code != 200:
        return "Error retreiving user data", status_code

    user_id = response["Item"]["id"]

    response = current_app.user_database.get_user_data(user_id)

    status_code = response["ResponseMetadata"]["HTTPStatusCode"]
    if status_code != 200:
        return "Error retrieving user data", status_code

    user = response["Item"]

    if user is not None and check_password_hash(user["password"], password):
        token = generate_token(username)
        return jsonify({"token": token}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401


# TODO: make this simpler
# flake8: noqa: C901
@bp.route("/resetPassword", methods=["GET", "POST"])
def reset_password():
    if request.method == "GET":
        email = request.args.get("email")
        if email is None:
            return "No email submitted", 400

        response = current_app.user_database.get_id_for_email(email)
        status_code = response["ResponseMetadata"]["HTTPStatusCode"]
        if status_code != 200:
            return "Error retrieving user data", status_code

        user_id = response["Item"]["id"]

        response = current_app.user_database.get_user_data(user_id)
        status_code = response["ResponseMetadata"]["HTTPStatusCode"]
        if status_code != 200:
            return "Error retrieving user data", status_code

        user = response["Item"]

        reset_guid = user["resetGuid"]
        current_app.email_manager.send_reset_code(email, reset_guid)

        return "OK", 200

    elif request.method == "POST":
        username = request.json.get("username")
        password = request.json.get("password")
        reset_guid = request.json.get("resetGuid")

        if username == "" or username is None:
            return "Username empty", 400
        if password == "" or password is None:
            return "password empty", 400
        if reset_guid == "" or reset_guid is None:
            return "reset_guid empty", 400

        response = current_app.user_database.get_id_for_username(username)
        status_code = response["ResponseMetadata"]["HTTPStatusCode"]
        if status_code != 200:
            return "Error retreiving user data", status_code

        user_id = response["Item"]["id"]

        response = current_app.user_database.get_user_data(user_id)
        status_code = response["ResponseMetadata"]["HTTPStatusCode"]
        if status_code != 200:
            return "Error retrieving user data", status_code

        user = response["Item"]
        if user["resetGuid"] != reset_guid:
            return "Invalid reset code", 400

        current_app.user_database.update_password(
            user["id"], generate_password_hash(password), str(uuid.uuid4())
        )

        token = generate_token(username)

        return token, 200


def generate_reset_password_email(email: str) -> str:
    response = current_app.user_database.get_id_for_email(email)
    status_code = response["ResponseMetadata"]["HTTPStatusCode"]
    if status_code != 200:
        return "Error retrieving user data", status_code

    reset_guid = response["Item"]["resetGuid"]

    reset_email_body = f"Your reset code is:\n{reset_guid}"
    return reset_email_body


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({"error": "Token is missing"}), 401

        # Check if the header starts with 'Bearer '
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Invalid token scheme"}), 401

        token = auth_header.split(" ")[1]  # Extract the token value

        # Verify and decode the token
        decoded = verify_token(token)

        if not decoded:
            return jsonify({"error": "Invalid token"}), 401

        # Token is valid, proceed with the protected route
        return f(*args, **kwargs)

    return decorated
