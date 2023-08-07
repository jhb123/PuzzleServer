import pytest

from moto import mock_ses

from flaskr import EmailManager, CloudStorage, PuzzleDatabase, UserDatabase, create_app


@mock_ses
@pytest.fixture()
def app():
    # We need to create the bucket since this is all in Moto's 'virtual' AWS account
    # conn.create_bucket(Bucket="jhb-crossword")

    email_manager = EmailManager()
    cloud_storage = CloudStorage()
    database = PuzzleDatabase()
    user_database = UserDatabase()

    app = create_app(email_manager, cloud_storage, database, user_database)
    app.config.update(
        {
            "TESTING": True,
        }
    )

    yield app

    # clean up / reset resources here


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


def test_hello_text(client):
    response = client.get("/hello")
    assert response.text == "Hello, World!"


def test_hello_status(client):
    response = client.get("/hello")
    assert response.status == "200 OK"
