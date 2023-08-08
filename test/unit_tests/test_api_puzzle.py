import json
import pytest


class TestPuzzleAPI:
    def test_post_search_puzzle_no_token_message(self, flask_client, new_user):
        flask_client.post("/auth/register", json=new_user)
        # token = json.loads(response.text)["token"]

        response = flask_client.post(
            "/puzzles/search",
            json={"id": "puzzle_id"},
        )

        assert response.json["error"] == "Token is missing"

    def test_post_search_puzzle_no_token_status(self, flask_client, new_user):
        flask_client.post("/auth/register", json=new_user)
        # token = json.loads(response.text)["token"]

        response = flask_client.post(
            "/puzzles/search",
            json={"id": "puzzle_id"},
        )

        assert response.status == "401 UNAUTHORIZED"

    def test_search_puzzle_invalid_token_scheme(self, flask_client, new_user):
        response = flask_client.post("/auth/register", json=new_user)
        token = json.loads(response.text)["token"]

        response = flask_client.post(
            "/puzzles/search",
            json={"id": "puzzle_id"},
            headers={"Authorization": token},
        )

        assert response.json["error"] == "Invalid token scheme"

    def test_search_puzzle_invalid_token_scheme_code(self, flask_client, new_user):
        response = flask_client.post("/auth/register", json=new_user)

        token = json.loads(response.text)["token"]

        response = flask_client.post(
            "/puzzles/search",
            json={"id": "puzzle_id"},
            headers={"Authorization": token},
        )

        assert response.status == "401 UNAUTHORIZED"

    @pytest.mark.parametrize("test_input", [None, "", "not a valid token code"])
    def test_search_puzzle_invalid_token(self, flask_client, test_input, new_user):
        response = flask_client.post("/auth/register", json=new_user)

        response = flask_client.post(
            "/puzzles/search",
            json={"id": "puzzle_id"},
            headers={"Authorization": f"Bearer {test_input}"},
        )

        assert response.status == "401 UNAUTHORIZED"

    @pytest.mark.parametrize("test_input", ["test", None, 1, True, "asdasd"])
    def test_search_puzzle_invalid_puzzle_id(self, flask_client, test_input, new_user):
        response = flask_client.post("/auth/register", json=new_user)

        token = json.loads(response.text)["token"]

        response = flask_client.post(
            "/puzzles/search",
            json={"id": test_input},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status == "404 NOT FOUND"

    def test_upload_valid_puzzle_status(self, flask_client, test_data_dir, new_user):
        response = flask_client.post("/auth/register", json=new_user)

        token = json.loads(response.text)["token"]

        data = {
            "id": "123",
            "timeCreated": "28/5/2023 12:35:36",
            "lastModified": "28/5/2023 13:35:36",
            "image": (test_data_dir.joinpath("test.png")).open("rb"),
            "puzzle": (test_data_dir.joinpath("test.json")).open("rb"),
        }

        response = flask_client.post(
            "/puzzles/upload", data=data, headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status == "200 OK"

    def test_post_search_valid_puzzle_status(
        self, flask_client, test_data_dir, new_user
    ):
        response = flask_client.post("/auth/register", json=new_user)

        token = json.loads(response.text)["token"]

        data = {
            "id": "123",
            "timeCreated": "28/5/2023 12:35:36",
            "lastModified": "28/5/2023 13:35:36",
            "image": (test_data_dir.joinpath("test.png")).open("rb"),
            "puzzle": (test_data_dir.joinpath("test.json")).open("rb"),
        }

        response = flask_client.post(
            "/puzzles/upload", data=data, headers={"Authorization": f"Bearer {token}"}
        )

        response = flask_client.post(
            "/puzzles/search",
            json={"id": "123"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status == "200 OK"

    def test_get_search_valid_puzzle_status(
        self, flask_client, test_data_dir, new_user
    ):
        response = flask_client.post("/auth/register", json=new_user)

        token = json.loads(response.text)["token"]

        data = {
            "id": "123",
            "timeCreated": "28/5/2023 12:35:36",
            "lastModified": "28/5/2023 13:35:36",
            "image": (test_data_dir.joinpath("test.png")).open("rb"),
            "puzzle": (test_data_dir.joinpath("test.json")).open("rb"),
        }

        response = flask_client.post(
            "/puzzles/upload", data=data, headers={"Authorization": f"Bearer {token}"}
        )

        response = flask_client.get(
            "/puzzles/search",
            query_string={"id": "123"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status == "200 OK"
