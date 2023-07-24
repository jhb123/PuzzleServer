import json
import os
import zipfile
from io import BytesIO

from botocore.exceptions import ClientError
from flask import Blueprint, current_app, send_file, request

from flaskr import cloud_storage
from flaskr.auth import token_required
from flaskr.db import get_db

bp = Blueprint("puzzles", __name__, url_prefix="/puzzles")


@bp.route("/search", methods=["GET", "POST"])
@token_required
def search():
    if request.method == "POST":
        puzzle_id = request.json.get("id")
    elif request.method == "GET":
        puzzle_id = request.args.get("id")

    # puzzle_id = f'{puzzle_id}'

    db = get_db()
    current_app.logger.info(f"getting {puzzle_id}")

    puzzle = db.execute(
        "SELECT * FROM puzzle_table WHERE id = ?", (puzzle_id,)
    ).fetchone()
    #
    if puzzle is None:
        return "No resource found", 404
    current_app.logger.info(puzzle["id"])


    try:
        puzzle_image = cloud_storage.download_image(f"{puzzle_id}.png")
    except ClientError:
        return "No resource found", 404
    try:
        puzzle_json = cloud_storage.download_image(f"{puzzle_id}.json")
    except ClientError:
        return "No resource found", 404
    
    files = [
        (f"{puzzle_id}.png", puzzle_image ),
        (f"{puzzle_id}.json", puzzle_json),
    ]

    current_app.logger.info(f"got files")


    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, "w") as zf:
        for individualFile in files:
            current_app.logger.info(f"zipping {individualFile[0]}")
            with individualFile[1] as f:
                zf.writestr(individualFile[0], f.read())
        zf.writestr("meta_data.json", json.dumps(dict(puzzle)))
    memory_file.seek(0)
    return send_file(
        memory_file, download_name="puzzle.zip", mimetype="application/zip"
    )


@bp.route("/upload", methods=["POST"])
@token_required
def upload():
    puzzleFile = request.files["puzzle"]
    imageFile = request.files["image"]
    id = request.form.get("id")
    time_created = request.form.get("timeCreated")
    last_modified = request.form.get("lastModified")

    current_app.logger.info(id)
    current_app.logger.info(time_created)
    current_app.logger.info(last_modified)

    sql_query = """
        INSERT OR REPLACE INTO puzzle_table
        (id, puzzle, timeCreated, lastModified,puzzleIcon)
        VALUES (?, ?, ?, ? ,?)
    """
    data = (id, puzzleFile.filename, time_created, last_modified, imageFile.filename)
    db = get_db()
    try:
        # TODO: replace with cloud storage.

        cloud_storage.upload_image(imageFile)
        cloud_storage.upload_puzzle_json(puzzleFile)

        db.execute(sql_query, data)
        db.commit()
        current_app.logger.info(f"uploaded {id}")
        return "OK", 200

    except Exception as e:
        current_app.logger.error(e)
        return 500
