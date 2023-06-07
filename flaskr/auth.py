import os
from functools import wraps
import jwt
from flask import request, jsonify
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from email.message import EmailMessage
import uuid

bp = Blueprint('auth', __name__, url_prefix='/auth')

# Secret key used to sign and verify the JWTs
secret_key = 'iLoveCats'


@bp.route('/register', methods=['POST'])
def register():

    username = request.json.get('username')
    password = request.json.get('password')
    email = request.json.get('email')
    db = get_db()
    error = None

    if not username:
        error = 'Username is required.'
    elif not password:
        error = 'Password is required.'
    elif not email:
        error = 'email is required.'

    if error is not None:
        return error, 400

    else:
        try:
            db.execute(
                "INSERT INTO user (username, password, email, resetGuid) VALUES (?, ?, ?, ?)",
                (username, generate_password_hash(password), email, str(uuid.uuid4())),
            )
            db.commit()
            return "Created new user", 201
        except db.IntegrityError as e:
            # figure out how to tell if its username or email which is conflicted.
            error = "username or email already registered"
            return error, 409


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# Generate a token for a given user
def generate_token(username):
    token = jwt.encode({'username': username}, secret_key, algorithm='HS256')
    return token


# Verify and decode a token
def verify_token(token):
    try:
        decoded = jwt.decode(token, secret_key, algorithms=['HS256'])
        return decoded
    except jwt.InvalidTokenError:
        return None


# Route for user login
@bp.route('/login2', methods=['POST'])
def login2():
    # Authenticate the user (e.g., check username and password)
    # If authentication is successful, generate a token
    username = request.json.get('username')
    password = request.json.get('password')

    db = get_db()

    user = db.execute(
        'SELECT * FROM user WHERE username = ?', (username,)
    ).fetchone()

    if user is not None and check_password_hash(user['password'], password):
        token = generate_token(username)
        return jsonify({'token': token}), 200
    else:
        error = 'Incorrect username.'
        return jsonify({'error': 'Invalid credentials'}), 401


@bp.route('/forgotPassword', methods=['POST'])
def forgot_password():
    # Authenticate the user (e.g., check username and password)
    # If authentication is successful, generate a token
    username = request.json.get('username')

    db = get_db()

    user = db.execute(
        'SELECT email FROM user WHERE username = ?', (username,)
    ).fetchone()

    return 200


@bp.route('/resetPassword', methods=['GET', "POST"])
def reset_password():
    if request.method == 'GET':

        email = request.args.get("email")
        try:
            email_body = generate_reset_password_email(email)
            send_reset_password_email(email, email_body)
            return "Ok", 200
        except TypeError as e:
            current_app.logging.warning(e)
            return "No such user", 404

    elif request.method == "POST":

        username = request.json.get('username')
        password = request.json.get('password')
        reset_guid = request.json.get('resetGuid')

        db = get_db()

        # check valid reset code
        userd_data = db.execute(
            'SELECT * FROM user WHERE resetGuid = ?', (reset_guid,)
        ).fetchone()

        current_app.logger.info(f"Reset code for {userd_data['email']} received.")
        current_app.logger.info(f"trying to use {password} for new password")

        # update user with valid reset code
        cursor = db.cursor()
        cursor.execute(
            "UPDATE user SET password = ? WHERE resetGuid is ?",
            (generate_password_hash(password), reset_guid)
        )
        db.commit()

        newGuid = str(uuid.uuid4())
        cursor.execute(
            'UPDATE user SET resetGuid = ? WHERE username is ?',
            (newGuid, username)
        )
        db.commit()
        current_app.logger.info(f"new update code {newGuid}")


        # cursor.execute('''UPDATE books SET price = ? WHERE id = ?''', (newPrice, book_id))

        return "OK", 200


def generate_reset_password_email(email: str) -> str:
    db = get_db()

    reset_guid = db.execute(
       'SELECT * FROM user WHERE email = ?', (email,)
    ).fetchone()
    # send a deep link?
    # reset_email_body = f"Please follow {request.base_url}?reset={reset_guid['resetGuid']}"
    reset_email_body = f"Your reset code is:\n{reset_guid['resetGuid']}"
    return reset_email_body


def send_reset_password_email(email: str, email_body: str):
    SCOPES = ["https://mail.google.com/"]

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])

        message = EmailMessage()
        message.set_content(email_body)
        message['To'] = email
        message['From'] = 'crosswordapp26@gmail.com'
        message['Subject'] = 'Reset your password'

        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()) \
            .decode()

        create_message = {
            'raw': encoded_message
        }
        # pylint: disable=E1101
        send_message = (service.users().messages().send
                        (userId="me", body=create_message).execute())
        print(F'Message Id: {send_message["id"]}')


    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')

    return 0


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return jsonify({'error': 'Token is missing'}), 401

        # Check if the header starts with 'Bearer '
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Invalid token scheme'}), 401

        token = auth_header.split(' ')[1]  # Extract the token value

        # Verify and decode the token
        decoded = verify_token(token)

        if not decoded:
            return jsonify({'error': 'Invalid token'}), 401

        # Token is valid, proceed with the protected route
        return f(*args, **kwargs)

    return decorated

