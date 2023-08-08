def test_hello_text(flask_client):
    response = flask_client.get("/hello")
    assert response.text == "Hello, World!"


def test_hello_status(flask_client):
    response = flask_client.get("/hello")
    assert response.status == "200 OK"
