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
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    app_dir_path = os.path.dirname(os.path.realpath(__file__))


    app.config["REDIS_URL"] = "redis://localhost"
    app.config['ICON_UPLOAD_FOLDER'] = f"{app_dir_path}/uploads/icons"
    app.config['PUZZLE_UPLOAD_FOLDER'] = f"{app_dir_path}/uploads/puzzles"
    app.config['ZIP_FOLDER'] = f"{app_dir_path}/uploads/zips"


    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.register_blueprint(sse, url_prefix='/stream')


    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/test_sockets")
    def test_sockets():
        return render_template("test_sockets.html")

    @app.route('/test_sse')
    def test_sse():
        return render_template("test_sse.html")

    # @app.route('/test_sse_ping')
    # def index():
    #     sse.publish({"message": "Hello!"}, type='greeting')
    #     return 'Hello, World!'

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        sse.publish({"message": "Hello!"}, type='greeting')
        app.logger.info("hello test sent")
        # socketio.emit("my response", 'Someone went to /hello')
        return 'Hello, World!'

    def get_message():
        time.sleep(0.1)
        return time.ctime(time.time())

    @app.route("/testStream")
    def stream():
        def event_stream():
            for i in range(5):
                time.sleep(0.1)
                app.logger.info(i)
                yield f"{i}"

        return stream_with_context(event_stream())
        # return event_stream(), {"Content-Type": "text/plain"}

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import puzzles
    app.register_blueprint(puzzles.bp)

    # socket_app = SocketIO(app)

    @socketio.on('connect')
    def handle_connection(event):
        app.logger.info("device connected")
        app.logger.info(event)

        emit("my response", 'Connected')

    @socketio.on('my event')
    def handle_message(event):
        app.logger.info(event["data"])
        emit("my response", 'Connected')

    socketio.init_app(app)

    return app
