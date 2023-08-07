#  TODO: are these integration tests?
import pytest


class TestUserDatabase:
    @pytest.mark.parametrize(
        "key, val",
        [
            ("id", "test"),
            ("username", "uname"),
            ("password", "pword"),
            ("email", "email@addr.com"),
            ("resetGuid", "123"),
        ],
    )
    def test_add_user_main_database(
        self, fake_crossword_user_databases, user_db_backend, key, val
    ):
        fake_crossword_user_databases.register_new_user(
            user_id="test",
            username="uname",
            password="pword",
            email="email@addr.com",
            reset_guid="123",
        )
        data = user_db_backend.get_item("crossword-userdata", {"id": {"S": "test"}})
        assert data.attrs[key].value == val

    def test_add_user_email_database(
        self, fake_crossword_user_databases, user_db_backend
    ):
        fake_crossword_user_databases.register_new_user(
            user_id="test",
            username="uname",
            password="pword",
            email="email@addr.com",
            reset_guid="123",
        )
        data = user_db_backend.get_item(
            "crossword-emails", {"email": {"S": "email@addr.com"}}
        )
        assert data.attrs["id"].value == "test"

    def test_add_user_username_database(
        self, fake_crossword_user_databases, user_db_backend
    ):
        fake_crossword_user_databases.register_new_user(
            user_id="test",
            username="uname",
            password="pword",
            email="email@addr.com",
            reset_guid="123",
        )
        data = user_db_backend.get_item(
            "crossword-usernames", {"username": {"S": "uname"}}
        )
        assert data.attrs["id"].value == "test"

    def test_get_user_by_id(self, fake_crossword_user_databases, user_db_backend):
        fake_crossword_user_databases.register_new_user(
            user_id="test",
            username="uname",
            password="pword",
            email="email@addr.com",
            reset_guid="123",
        )
        response = fake_crossword_user_databases.get_id_for_username("uname")
        assert response["Item"]["id"] == "test"

    def test_get_id_for_email(self, fake_crossword_user_databases, user_db_backend):
        fake_crossword_user_databases.register_new_user(
            user_id="test",
            username="uname",
            password="pword",
            email="email@addr.com",
            reset_guid="123",
        )
        response = fake_crossword_user_databases.get_id_for_email("email@addr.com")
        assert response["Item"]["id"] == "test"

    @pytest.mark.parametrize(
        "key, val",
        [
            ("id", "test"),
            ("username", "uname"),
            ("password", "pword"),
            ("email", "email@addr.com"),
            ("resetGuid", "123"),
        ],
    )
    def test_get_user_data(
        self, fake_crossword_user_databases, user_db_backend, key, val
    ):
        fake_crossword_user_databases.register_new_user(
            user_id="test",
            username="uname",
            password="pword",
            email="email@addr.com",
            reset_guid="123",
        )
        response = fake_crossword_user_databases.get_user_data("test")
        assert response["Item"][key] == val

    def test_add_duplicate_username(self, fake_crossword_user_databases):
        fake_crossword_user_databases.register_new_user(
            user_id="test",
            username="uname",
            password="pword",
            email="email@addr.com",
            reset_guid="123",
        )

        registered_second_user = fake_crossword_user_databases.register_new_user(
            user_id="test1",
            username="uname",
            password="pword",
            email="anther_email@addr.com",
            reset_guid="123",
        )

        # db_backend.get_item("crossword-userdata", {"id": {"S": "test1"}})
        assert not registered_second_user

    def test_add_duplicate_username_backend(
        self, fake_crossword_user_databases, user_db_backend
    ):
        fake_crossword_user_databases.register_new_user(
            user_id="expected_id",
            username="uname",
            password="pword",
            email="email@addr.com",
            reset_guid="123",
        )

        fake_crossword_user_databases.register_new_user(
            user_id="second_user_id",
            username="uname",
            password="pword",
            email="anther_email@addr.com",
            reset_guid="123",
        )

        data = user_db_backend.get_item(
            "crossword-usernames", {"username": {"S": "uname"}}
        )
        assert data.attrs["id"].value == "expected_id"

    def test_add_duplicate_email(self, fake_crossword_user_databases, user_db_backend):
        fake_crossword_user_databases.register_new_user(
            user_id="expected_id",
            username="uname",
            password="pword",
            email="email@addr.com",
            reset_guid="123",
        )

        fake_crossword_user_databases.register_new_user(
            user_id="second_user_id",
            username="another_uname",
            password="pword",
            email="email@addr.com",
            reset_guid="123",
        )

        data = user_db_backend.get_item(
            "crossword-emails", {"email": {"S": "email@addr.com"}}
        )
        assert data.attrs["id"].value == "expected_id"

    def test_delete_email(self, fake_crossword_user_databases, user_db_backend):
        fake_crossword_user_databases.register_new_user(
            user_id="expected_id",
            username="uname",
            password="pword",
            email="email@addr.com",
            reset_guid="123",
        )

        fake_crossword_user_databases.delete_email("email@addr.com")

        data = user_db_backend.get_item(
            "crossword-emails", {"email": {"S": "email@addr.com"}}
        )
        assert data is None

    @pytest.mark.parametrize(
        "key, val",
        [
            ("id", "test"),
            ("username", "uname"),
            ("password", "pword2"),
            ("email", "email@addr.com"),
            ("resetGuid", "456"),
        ],
    )
    def test_update_password(
        self, fake_crossword_user_databases, user_db_backend, key, val
    ):
        fake_crossword_user_databases.register_new_user(
            user_id="test",
            username="uname",
            password="pword",
            email="email@addr.com",
            reset_guid="123",
        )

        fake_crossword_user_databases.update_password("test", "pword2", "456")
        data = user_db_backend.get_item("crossword-userdata", {"id": {"S": "test"}})
        assert data.attrs[key].value == val
