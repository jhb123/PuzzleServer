import json
import os
import time

import socketio
from flask_socketio import SocketIO, send, emit
from flask import Flask, render_template, request, redirect, url_for, Response, stream_with_context
from flask_sse import sse

socketio = SocketIO()


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    # app.config.from_file("../config.json", load=json.load)

    app.config.from_mapping(
        SECRET_KEY='dev',
        JWT_KEY='iLoveCats',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    app_dir_path = os.path.dirname(os.path.realpath(__file__))

    app.config['ICON_UPLOAD_FOLDER'] = f"{app_dir_path}/uploads/icons"
    app.config['PUZZLE_UPLOAD_FOLDER'] = f"{app_dir_path}/uploads/puzzles"

    if not os.path.isdir(app.config['ICON_UPLOAD_FOLDER']):
        app.logger.info("Creating icon upload folder")
        os.makedirs(app.config['ICON_UPLOAD_FOLDER'])
    if not os.path.isdir(app.config['PUZZLE_UPLOAD_FOLDER']):
        app.logger.info("Creating icon upload folder")
        os.makedirs(app.config['PUZZLE_UPLOAD_FOLDER'])

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.logger.info('Loading config from pyfile')
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route("/")
    def index():
        return render_template("index.html")

    # a test route
    @app.route('/hello')
    def hello():
        app.logger.info("hello test sent")
        return 'Hello, World!'

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import puzzles
    app.register_blueprint(puzzles.bp)

    return app
