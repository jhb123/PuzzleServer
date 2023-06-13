import os

import socketio
from flask_socketio import SocketIO, send, emit
from flask import Flask, render_template
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
    app.config["REDIS_URL"] = "redis://localhost"

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
        socketio.emit("my response", 'Someone went to /hello')
        return 'Hello, World!'

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import puzzles
    app.register_blueprint(puzzles.bp)

    # socket_app = SocketIO(app)

    @socketio.on('my event')
    def handle_message(event):
        app.logger.info(event["data"])
        emit("my response", 'Connected')

    socketio.init_app(app)

    return app
