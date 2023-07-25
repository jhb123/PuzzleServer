import os

from flask import Flask

from flaskr.cloud.database import PuzzleDatabase, UserDatabase
from flaskr.cloud.email import EmailManager
from flaskr.cloud.storage import CloudStorage

email_manager = EmailManager()
cloud_storage = CloudStorage()
database = PuzzleDatabase()
user_database = UserDatabase()

def create_app(test_config=None):
    print(".")
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    # app.config.from_file("../config.json", load=json.load)

    app.config.from_mapping(
        SECRET_KEY="dev",
        JWT_KEY="iLoveCats",
        DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
    )

    app_dir_path = os.path.dirname(os.path.realpath(__file__))

    secret_configs = "/".join(app_dir_path.split("/")[0:-1])

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.logger.info("Loading config from pyfile")
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a test route
    @app.route("/hello")
    def hello():
        app.logger.info("hello test sent")
        return "Hello, World!"

    from . import db

    db.init_app(app)

    from . import auth

    app.register_blueprint(auth.bp)

    from . import puzzles

    app.register_blueprint(puzzles.bp)

    return app
