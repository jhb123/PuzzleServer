import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('puzzles', __name__, url_prefix='/puzzles')


@bp.route('/search', methods=('GET', 'POST'))
def register():
    # if request.method == 'POST':
    #     puzzle_id = request.form['puzzle_id']
    #     db = get_db()
    #     error = None
    #
    #     if not puzzle_id:
    #         error = 'puzzle ID is required.'
    #
    #     if error is None:
    #         try:
    #             db.execute("SELECT * WHERE id=(?)",puzzle_id)
    #             #db.commit()
    #             result = db.fetchall()
    #             for row in result:
    #                 print(row)
    #
    #         except db.IntegrityError:
    #             error = f"{puzzle_id} is not found."
    #     else:
    #         return redirect(url_for("auth.login"))
    #
    #     flash(error)
    db = get_db()
    curr = db.cursor()
    curr.execute("SELECT * From puzzle_table WHERE id='20/5/2023 08:42:09'")
    result = curr.fetchall()
    for row in result:
        print(row)

    return f"{result[0][1]}"
