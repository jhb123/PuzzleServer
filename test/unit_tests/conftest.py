import os
from pathlib import Path
from typing import List, Tuple
import logging

import boto3
import pytest
from moto import mock_ses, mock_dynamodb, mock_s3, mock_all
from moto.core import DEFAULT_ACCOUNT_ID
from moto.dynamodb.models import DynamoDBBackend, dynamodb_backends
from moto.s3 import s3_backends
from moto.s3.models import S3Backend
from moto.ses import ses_backends
from moto.ses.models import Message

from flaskr import create_app, EmailManager, PuzzleDatabase, CloudStorage, UserDatabase

logger = logging.getLogger(__name__)


@pytest.fixture()
def app(fake_all_services):
    # We need to create the bucket since this is all in Moto's 'virtual' AWS account
    # conn.create_bucket(Bucket="jhb-crossword")

    user_database: UserDatabase = fake_all_services[0]
    database: PuzzleDatabase = fake_all_services[1]
    email_manager: EmailManager = fake_all_services[2]
    cloud_storage: CloudStorage = fake_all_services[3]

    config = {"TESTING": True, "SECRET_KEY": "dev", "JWT_KEY": "iLoveCats"}
    app = create_app(
        email_manager=email_manager,
        cloud_storage=cloud_storage,
        puzzle_database=database,
        user_database=user_database,
        test_config=config,
    )

    yield app

    # clean up / reset resources here


@pytest.fixture()
def flask_client(app):
    return app.test_client()


@pytest.fixture(scope="module")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"


@pytest.fixture
def fake_email_manager(aws_credentials):
    with mock_ses():
        conn = boto3.client("ses", region_name="eu-north-1")
        conn.verify_email_address(EmailAddress="crosswordapp26@gmail.com")
        yield EmailManager()


@pytest.fixture
def messages(aws_credentials):
    ses_backend = ses_backends[DEFAULT_ACCOUNT_ID]["eu-north-1"]
    messages: List[Message] = ses_backend.sent_messages
    yield messages


@pytest.fixture
def test_data_dir():
    test_dir = Path(__file__).parent.parent
    test_data_directory = test_dir.joinpath("test_data")
    yield test_data_directory


@pytest.fixture
def db_backend(aws_credentials):
    db_backend: DynamoDBBackend = dynamodb_backends[DEFAULT_ACCOUNT_ID]["eu-north-1"]
    yield db_backend


@pytest.fixture(scope="module")
def crossword_table_params():
    table = {
        "TableName": "crosswords",
        "KeySchema": [
            {"AttributeName": "id", "KeyType": "HASH"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "id", "AttributeType": "S"},
        ],
        "ProvisionedThroughput": {
            "ReadCapacityUnits": 10,
            "WriteCapacityUnits": 10,
        },
    }
    yield table


@pytest.fixture(scope="module")
def user_data_table_params():
    table = {
        "TableName": "crossword-userdata",
        "KeySchema": [
            {"AttributeName": "id", "KeyType": "HASH"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "id", "AttributeType": "S"},
        ],
        "ProvisionedThroughput": {
            "ReadCapacityUnits": 10,
            "WriteCapacityUnits": 10,
        },
    }
    yield table


@pytest.fixture(scope="module")
def user_name_table_params():
    table = {
        "TableName": "crossword-usernames",
        "KeySchema": [
            {"AttributeName": "username", "KeyType": "HASH"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "username", "AttributeType": "S"},
        ],
        "ProvisionedThroughput": {
            "ReadCapacityUnits": 10,
            "WriteCapacityUnits": 10,
        },
    }
    yield table


@pytest.fixture(scope="module")
def user_email_table_params():
    table = {
        "TableName": "crossword-emails",
        "KeySchema": [
            {"AttributeName": "email", "KeyType": "HASH"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "email", "AttributeType": "S"},
        ],
        "ProvisionedThroughput": {
            "ReadCapacityUnits": 10,
            "WriteCapacityUnits": 10,
        },
    }
    yield table


@pytest.fixture
def fake_crossword_db(aws_credentials, crossword_table_params):
    with mock_dynamodb():
        conn = boto3.client("dynamodb")
        conn.create_table(**crossword_table_params)

        yield PuzzleDatabase()


@pytest.fixture
def puzzle_test_data():
    data = {
        "id": {"S": "test"},
        "puzzle": {"S": "file.json"},
        "timeCreated": {"S": "1/1/1 1:11 UTC+1"},
        "lastModified": {"S": "2/2/2 2:22 UTC+2"},
        "icon": {"S": "file.png"},
    }

    return data


@pytest.fixture
def s3_backend(aws_credentials):
    s3_backend: S3Backend = s3_backends[DEFAULT_ACCOUNT_ID]["global"]
    yield s3_backend


@pytest.fixture
def fake_storage(aws_credentials):
    with mock_s3():
        conn = boto3.client("s3", region_name="us-east-1")
        conn.create_bucket(Bucket="jhb-crossword")

        yield CloudStorage()


@pytest.fixture
def user_db_backend(aws_credentials):
    db_backend: DynamoDBBackend = dynamodb_backends[DEFAULT_ACCOUNT_ID]["eu-north-1"]
    yield db_backend


@pytest.fixture
def fake_crossword_user_databases(
    aws_credentials,
    user_data_table_params,
    user_name_table_params,
    user_email_table_params,
):
    with mock_dynamodb():
        conn = boto3.client("dynamodb", region_name="eu-north-1")
        conn.create_table(**user_data_table_params)
        conn.create_table(**user_email_table_params)
        conn.create_table(**user_name_table_params)

        yield UserDatabase()


# @pytest.fixture
# def user_test_data():
#     userdata = {
#         "id": {"S": "test"},
#         "username": {"S": "uname"},
#         "password": {"S": "pword"},
#         "email": {"S": "email@addr.com"},
#         "resetGuid": {"S": "123"},
#     }
#
#     username = {
#         "username": {"S": "uname"},
#         "id": {"S": "test"},
#     }
#     email = {
#         "email": {"S": "email@addr.com"},
#         "id": {"S": "test"},
#     }
#
#     return userdata, username, email


# @pytest.fixture
# def fake_all_databases(
#     aws_credentials,
#     user_email_table_params,
#     user_data_table_params,
#     crossword_table_params,
#     user_name_table_params,
# ) -> Tuple[UserDatabase, PuzzleDatabase]:
#     with mock_dynamodb():
#         conn = boto3.client("dynamodb")
#         conn.create_table(**user_data_table_params)
#         conn.create_table(**user_email_table_params)
#         conn.create_table(**user_name_table_params)
#         conn.create_table(**crossword_table_params)
#
#         yield UserDatabase(), PuzzleDatabase()


@pytest.fixture(scope="module")
def fake_all_services(
    aws_credentials,
    user_email_table_params,
    user_data_table_params,
    crossword_table_params,
    user_name_table_params,
) -> Tuple[UserDatabase, PuzzleDatabase, EmailManager, CloudStorage]:
    with mock_all():
        conn = boto3.client("dynamodb", region_name="eu-north-1")
        conn.create_table(**user_data_table_params)
        conn.create_table(**user_email_table_params)
        conn.create_table(**user_name_table_params)
        conn.create_table(**crossword_table_params)

        conn = boto3.client("ses", region_name="eu-north-1")
        conn.verify_email_address(EmailAddress="crosswordapp26@gmail.com")

        conn = boto3.client("s3", region_name="us-east-1")
        conn.create_bucket(Bucket="jhb-crossword")

        yield UserDatabase(), PuzzleDatabase(), EmailManager(), CloudStorage()


@pytest.fixture
def new_user(fake_all_services):
    yield {"username": "uname", "password": "pword", "email": "email@addr.com"}
    user_db = fake_all_services[0]

    user_id = user_db.get_id_for_username("uname")["Item"]["id"]
    user_db.username_table.delete_item(Key={"username": "uname"})
    user_db.email_table.delete_item(Key={"email": "email@addr.com"})
    user_db.user_table.delete_item(Key={"id": user_id})


@pytest.fixture
def delete_emails(messages):
    yield
    messages.clear()
