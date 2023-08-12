from os import PathLike

from flask import Flask

from flaskr.cloud.database import PuzzleDatabase, UserDatabase
from flaskr.cloud.email import EmailManager
from flaskr.cloud.secrets import Secrets
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
    # create and configure the app
    app = PuzzleFlask(
        email_manager,
        cloud_storage,
        puzzle_database,
        user_database,
        import_name=__name__,
        instance_relative_config=True,
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        secrets = Secrets()
        app.logger.info("Loading config from dynamo")
        app.config.update(
            TESTING=False,
            SECRET_KEY=secrets.get_secret("SECRET_KEY"),
            JWT_KEY=secrets.get_secret("JWT_KEY"),
        )
    else:
        # load the test config if passed in
        app.config.update(
            TESTING=True,
            SECRET_KEY=test_config["SECRET_KEY"],
            JWT_KEY=test_config["JWT_KEY"],
        )

    @app.route("/")
    def index():
        return "Welcome to the Puzzle Server"

    # a test route
    @app.route("/hello")
    def hello():
        app.logger.info("hello test sent")
        return "Hello, World!"

    from . import auth

    app.register_blueprint(auth.bp)

    from . import puzzles

    app.register_blueprint(puzzles.bp)

    return app
