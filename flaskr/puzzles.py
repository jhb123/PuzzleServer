import functools
import json
import sqlite3

import flask
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify, app, current_app
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.auth import token_required
from flaskr.db import get_db

import logging

from flaskr.puzzle_data import PuzzleData

bp = Blueprint('puzzles', __name__, url_prefix='/puzzles')


@bp.route('/search', methods=['GET', 'POST'])
@token_required
def search():
    if flask.request.method == 'POST':
        puzzle_id = request.json.get('id')
    elif flask.request.method == 'GET':
        puzzle_id = request.args.get('id')

    db = get_db()

    puzzle = db.execute(
        'SELECT puzzle FROM puzzle_table WHERE id = ?', (puzzle_id,)
    ).fetchone()

    return json.loads(puzzle[0]), 200

@bp.route('/upload', methods=['POST'])
@token_required
def upload():
    id = request.json.get('id')
    puzzle = request.json.get('puzzle')

    # puzzle = PuzzleData(id,puzzle)

    sql = "INSERT INTO puzzle_table VALUES (?,?)"

    db = get_db()
    try:
        db.execute(sql, (id, json.dumps(puzzle)))
        db.commit()
        return "Created", 201
    except sqlite3.IntegrityError:
        # current_app.logger.warning(f"ID not unique")
        return" ID not unique", 409



