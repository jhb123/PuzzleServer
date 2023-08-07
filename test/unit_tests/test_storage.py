import os
from pathlib import Path
from typing import List, Tuple

import boto3
import pytest
from botocore.exceptions import ClientError
from moto import mock_s3
from moto.core import DEFAULT_ACCOUNT_ID

from moto.s3.models import S3Backend, s3_backends, FakeKey, FakeBucket
from werkzeug.datastructures import FileStorage

from flaskr import CloudStorage


@pytest.fixture
def test_data_dir():
    test_dir = Path(__file__).parent.parent
    test_data_directory = test_dir.joinpath("test_data")
    yield test_data_directory


@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"


@pytest.fixture
def backend(aws_credentials):
    s3_backend: S3Backend = s3_backends[DEFAULT_ACCOUNT_ID]["global"]
    yield s3_backend


@pytest.fixture
def fake_storage(aws_credentials):
    with mock_s3():
        conn = boto3.client("s3", region_name="us-east-1")
        conn.create_bucket(Bucket="jhb-crossword")

        yield CloudStorage()


def _pop_latest_item(fb: FakeBucket) -> Tuple[str, List[FakeKey]]:
    item: Tuple[str, List[FakeKey]] = fb.keys.popitem()
    return item


def pop_latest_item_content(fb: FakeBucket):
    item = _pop_latest_item(fb)
    return item[1][0].value


def pop_latest_item_name(fb: FakeBucket):
    item = _pop_latest_item(fb)
    return item[1][0].name


def pop_latest_item_key(fb: FakeBucket):
    item = _pop_latest_item(fb)
    return item[0]
    # print(item[1][0].value)


def test_invalid_puzzle_json_name(fake_storage):
    with pytest.raises(ClientError):
        fake_storage.download_puzzle_json("invalid_name.json")


def test_invalid_puzzle_image_name(fake_storage):
    with pytest.raises(ClientError):
        fake_storage.download_image("invalid_name.png")


def test_wrong_json_file_ext(fake_storage):
    with pytest.raises(ValueError):
        fake_storage.download_puzzle_json("invalid_name.png")


def test_wrong_image_file_ext(fake_storage):
    with pytest.raises(ValueError):
        fake_storage.download_image("invalid_name.jpeg")


def test_no_file_ext(fake_storage):
    with pytest.raises(ValueError):
        fake_storage.download_image("invalid_name")


@pytest.mark.parametrize("test_input", ["test.json"])
def test_upload_puzzle_file(fake_storage, test_data_dir, backend, test_input):
    with open(test_data_dir.joinpath(test_input), "rb") as local_file:
        local_content = local_file.read()
    file = FileStorage(open(test_data_dir.joinpath(test_input), "rb"), name=test_input)
    fake_storage.upload_puzzle_json(file)
    fb: FakeBucket = backend.get_bucket("jhb-crossword")
    uploaded_content = pop_latest_item_content(fb)
    assert local_content == uploaded_content


@pytest.mark.parametrize("test_input", ["test.json"])
def test_upload_image_file_wrong_format(
    fake_storage, test_data_dir, backend, test_input
):
    with pytest.raises(ValueError):
        file = FileStorage(
            open(test_data_dir.joinpath(test_input), "rb"), name=test_input
        )
        fake_storage.upload_image(file)


@pytest.mark.parametrize("test_input", ["test.png"])
def test_upload_puzzle_file_wrong_format(
    fake_storage, test_data_dir, backend, test_input
):
    with pytest.raises(ValueError):
        file = FileStorage(
            open(test_data_dir.joinpath(test_input), "rb"), name=test_input
        )
        fake_storage.upload_puzzle_json(file)


def test_upload_puzzle_file_none(fake_storage):
    with pytest.raises(ValueError):
        fake_storage.upload_puzzle_json(None)


@pytest.mark.parametrize(
    "test_input",
    [
        "invalid_clue_boxes.json",
        "invalid_clue_data.json",
        "missing_clues_1.json",
        "missing_clues_2.json",
        "missing_grid_size.json",
    ],
)
def test_invalid_json_upload(fake_storage, test_data_dir, test_input):
    file = FileStorage(open(test_data_dir.joinpath(test_input), "rb"), name=test_input)
    with pytest.raises(KeyError):
        fake_storage.upload_puzzle_json(file)


@pytest.mark.parametrize("test_input", ["test.png"])
def test_upload_image(fake_storage, test_data_dir, backend, test_input):
    with open(test_data_dir.joinpath(test_input), "rb") as local_file:
        local_content = local_file.read()
    file = FileStorage(open(test_data_dir.joinpath(test_input), "rb"), name=test_input)
    fake_storage.upload_image(file)
    fb: FakeBucket = backend.get_bucket("jhb-crossword")
    uploaded_content = pop_latest_item_content(fb)
    assert local_content == uploaded_content


# Can't version control this large image, maybe there's a better way to test this.
# @pytest.mark.parametrize("test_input", ["large_image.png"])
# def test_upload_big_image(fake_storage, test_data_dir, test_input):
#     file = FileStorage(
#       open(test_data_dir.joinpath(test_input), "rb"), name=test_input
#       )
#     with pytest.raises(ValueError):
#         fake_storage.upload_image(file)
