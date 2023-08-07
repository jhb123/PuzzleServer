def test_hello_text(client):
    response = client.get("/hello")
    assert response.text == "Hello, World!"


def test_hello_status(client):
    response = client.get("/hello")
    assert response.status == "200 OK"
