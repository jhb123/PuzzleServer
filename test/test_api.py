import pytest
from flaskr import create_app


@pytest.fixture()
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
    })

    # other setup can go here

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
