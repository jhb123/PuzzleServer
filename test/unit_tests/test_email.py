import string
from typing import List
import pytest
from moto.ses.models import Message
from flaskr.cloud.email import EmailStrings


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
def test_valid_reset_email_body(
    fake_email_manager, messages: List[Message], test_input
):
    fake_email_manager.send_reset_code("foo@bar.com", test_input)
    assert messages[0].body == EmailStrings.reset_body.format(test_input)


@pytest.mark.parametrize("test_input", ["", None])
def test_invalid_reset_email_body(fake_email_manager, test_input):
    with pytest.raises(ValueError):
        fake_email_manager.send_reset_code("foo@bar.com", test_input)


def test_email_strings(fake_email_manager, messages: List[Message]):
    fake_email_manager.send_reset_code("foo@bar.com", "abc")
    assert messages[0].subject == EmailStrings.reset_subject


def test_email_recipient(fake_email_manager, messages: List[Message]):
    fake_email_manager.send_reset_code("foo@bar.com", "abc")
    assert messages[0].destinations["ToAddresses"][0] == "foo@bar.com"


@pytest.mark.parametrize(
    "test_input,expected", [("ToAddresses", 1), ("CcAddresses", 0), ("BccAddresses", 0)]
)
def test_email_recipients(
    fake_email_manager, messages: List[Message], test_input, expected
):
    fake_email_manager.send_reset_code("foo@bar.com", "abc")
    assert len(messages[0].destinations[test_input]) == expected
