import os
import string
from typing import List

import boto3
import pytest
from moto import mock_ses
from moto.ses import ses_backends
from moto.core import DEFAULT_ACCOUNT_ID
from moto.ses.models import Message

from flaskr import EmailManager
from flaskr.cloud.email import EmailStrings


@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"


@pytest.fixture
def email_manager(aws_credentials):
    with mock_ses():
        conn = boto3.client("ses", region_name="eu-north-1")
        conn.verify_email_address(EmailAddress="crosswordapp26@gmail.com")
        yield EmailManager()


@pytest.fixture
def messages(aws_credentials):
    ses_backend = ses_backends[DEFAULT_ACCOUNT_ID]["eu-north-1"]
    messages: List[Message] = ses_backend.sent_messages
    yield messages


@pytest.mark.parametrize(
    "test_input",
    [
        "testcode",
        "1234-ghioj-23r2afg-412423",
        "0123456789",
        string.ascii_letters,
        string.punctuation,
        string.printable,
    ],
)
def test_valid_reset_email_body(email_manager, messages: List[Message], test_input):
    email_manager.send_reset_code("foo@bar.com", test_input)
    assert messages[0].body == EmailStrings.reset_body.format(test_input)


@pytest.mark.parametrize("test_input", ["", None])
def test_invalid_reset_email_body(email_manager, test_input):
    with pytest.raises(ValueError):
        email_manager.send_reset_code("foo@bar.com", test_input)


def test_email_strings(email_manager, messages: List[Message]):
    email_manager.send_reset_code("foo@bar.com", "abc")
    assert messages[0].subject == EmailStrings.reset_subject


def test_email_recipient(email_manager, messages: List[Message]):
    email_manager.send_reset_code("foo@bar.com", "abc")
    assert messages[0].destinations["ToAddresses"][0] == "foo@bar.com"


@pytest.mark.parametrize(
    "test_input,expected", [("ToAddresses", 1), ("CcAddresses", 0), ("BccAddresses", 0)]
)
def test_email_recipients(email_manager, messages: List[Message], test_input, expected):
    email_manager.send_reset_code("foo@bar.com", "abc")
    assert len(messages[0].destinations[test_input]) == expected
