import functools
import json

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.auth import token_required
from flaskr.db import get_db

bp = Blueprint('puzzles', __name__, url_prefix='/puzzles')


@bp.route('/search', methods=['POST'])
@token_required
def search():
    id = request.json.get('id')
    db = get_db()
    puzzle = db.execute(
        'SELECT * FROM puzzle_table WHERE id = ?', (id,)
    ).fetchone()

    #curr = db.cursor()
    #curr.execute(f"SELECT * From puzzle_table WHERE id='{id}'")
    #result = curr.fetchall()

    return json.loads(puzzle["puzzle"]), 200
