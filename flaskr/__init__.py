from os import PathLike, path, makedirs

from flask import Flask

from flaskr.cloud.database import PuzzleDatabase, UserDatabase
from flaskr.cloud.email import EmailManager
from flaskr.cloud.storage import CloudStorage


class PuzzleFlask(Flask):
    """
    This class provides dependency injection for the Flask app class.
    """

    def __init__(
        self,
        email_manager: EmailManager,
        cloud_storage: CloudStorage,
        puzzle_database: PuzzleDatabase,
        user_database: UserDatabase,
        import_name: str,
        static_url_path: str | None = None,
        static_folder: str | PathLike | None = "static",
        static_host: str | None = None,
        host_matching: bool = False,
        subdomain_matching: bool = False,
        template_folder: str | PathLike | None = "templates",
        instance_path: str | None = None,
        instance_relative_config: bool = False,
        root_path: str | None = None,
    ):
        super().__init__(
            import_name,
            static_url_path,
            static_folder,
            static_host,
            host_matching,
            subdomain_matching,
            template_folder,
            instance_path,
            instance_relative_config,
            root_path,
        )

        self.email_manager = email_manager
        self.cloud_storage = cloud_storage
        self.puzzle_database = puzzle_database
        self.user_database = user_database


def create_app(
    email_manager: EmailManager,
    cloud_storage: CloudStorage,
    puzzle_database: PuzzleDatabase,
    user_database: UserDatabase,
    test_config=None,
):
    print(".")
    # create and configure the app
    app = PuzzleFlask(
        email_manager,
        cloud_storage,
        puzzle_database,
        user_database,
        import_name=__name__,
        instance_relative_config=True,
    )
    # app.config.from_file("../config.json", load=json.load)

    app.config.from_mapping(
        SECRET_KEY="dev",
        JWT_KEY="iLoveCats",
        DATABASE=path.join(app.instance_path, "flaskr.sqlite"),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.logger.info("Loading config from pyfile")
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        makedirs(app.instance_path)
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
