import json
import zipfile
from io import BytesIO

from botocore.exceptions import ClientError
from flask import Blueprint, current_app, send_file, request

from flaskr.auth import token_required

bp = Blueprint("puzzles", __name__, url_prefix="/puzzles")

# TODO: simplify search


# flake8: noqa: C901
@bp.route("/search", methods=["GET", "POST"])
@token_required
def search():
    puzzle_id = None

    if request.method == "POST":
        puzzle_id = request.json.get("id")
    elif request.method == "GET":
        puzzle_id = request.args.get("id")

    # puzzle_id = f'{puzzle_id}'
    try:
        puzzle = current_app.puzzle_database.get_puzzle_meta_data(puzzle_id)
    except KeyError:
        return "Puzzle not found", 404
    except ClientError:
        return "Database Client error", 500
    if puzzle is None:
        return "No resource found", 404

    current_app.logger.info(puzzle["id"])
    puzzle_image_id = puzzle["icon"]
    puzzle_json_id = puzzle["puzzle"]
    try:
        puzzle_image = current_app.cloud_storage.download_image(puzzle_image_id)
    except ClientError:
        return f"Could not locate {puzzle_image_id}", 404
    try:
        puzzle_json = current_app.cloud_storage.download_puzzle_json(puzzle_json_id)
    except ClientError:
        return f"Could not locate {puzzle_json_id}", 404

    files = [
        (f"{puzzle_id}.png", puzzle_image),
        (f"{puzzle_id}.json", puzzle_json),
    ]

    current_app.logger.info("got files")

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
    puzzle_file = request.files["puzzle"]
    image_file = request.files["image"]
    puzzle_id = request.form.get("id")
    time_created = request.form.get("timeCreated")
    last_modified = request.form.get("lastModified")

    current_app.logger.info(puzzle_id)
    current_app.logger.info(time_created)
    current_app.logger.info(last_modified)

    try:
        current_app.cloud_storage.upload_image(image_file)
        current_app.cloud_storage.upload_puzzle_json(puzzle_file)
        current_app.puzzle_database.upload_puzzle_meta_data(
            puzzle_id,
            puzzle_file.filename,
            time_created,
            last_modified,
            image_file.filename,
        )
        current_app.logger.info(f"uploaded {puzzle_id}")
        return "OK", 200

    except ClientError as e:
        current_app.logger.exception(e)
        return 500
