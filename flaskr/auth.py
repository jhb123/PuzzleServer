from functools import wraps

import jwt
from flask import request, jsonify

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

# Secret key used to sign and verify the JWTs
secret_key = 'your_secret_key'


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')

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


@bp.route('/protected')
@token_required
def protected_route():
    # Your protected route logic goes here
    return 'Protected route accessed successfully'