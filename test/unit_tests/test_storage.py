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
    with pytest.raises(ClientError) as excinfo:
        fake_storage.download_puzzle_json("invalid_name.json")
    assert excinfo.type == ClientError


@pytest.mark.parametrize("fname", ["file.png"])
def test_missing_puzzle_image_name(fake_storage, fname):
    with pytest.raises(ClientError) as excinfo:
        fake_storage.download_image(fname)
    assert excinfo.type == ClientError


def test_upload_none_json(fake_storage):
    with pytest.raises(ValueError) as excinfo:
        fake_storage.upload_puzzle_json(None)
    assert excinfo.type == ValueError


def test_upload_none_image(fake_storage):
    with pytest.raises(ValueError) as excinfo:
        fake_storage.upload_image(None)
    assert excinfo.type == ValueError


@pytest.mark.parametrize("fname", ["file.png", "json", ".json", ".", ".json", "file."])
def test_wrong_json_file_ext(fake_storage, fname):
    with pytest.raises(ValueError) as excinfo:
        fake_storage.download_puzzle_json(fname)
    assert excinfo.type == ValueError


@pytest.mark.parametrize("fname", ["file.jpeg", "png", ".png", ".", ".jpeg", "file."])
def test_wrong_image_file_ext(fake_storage, fname):
    with pytest.raises(ValueError) as excinfo:
        fake_storage.download_image(fname)
    assert excinfo.type == ValueError


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
    with pytest.raises(ValueError) as excinfo:
        file = FileStorage(
            open(test_data_dir.joinpath(test_input), "rb"), name=test_input
        )
        fake_storage.upload_image(file)
    assert excinfo.type == ValueError


@pytest.mark.parametrize("test_input", ["test.png"])
def test_upload_json_file_wrong_format(
    fake_storage, test_data_dir, backend, test_input
):
    with pytest.raises(ValueError) as excinfo:
        file = FileStorage(
            open(test_data_dir.joinpath(test_input), "rb"), name=test_input
        )
        fake_storage.upload_puzzle_json(file)
    assert excinfo.type == ValueError


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
def test_invalid_json_keys_upload(fake_storage, test_data_dir, test_input):
    file = FileStorage(open(test_data_dir.joinpath(test_input), "rb"), name=test_input)
    with pytest.raises(KeyError) as excinfo:
        fake_storage.upload_puzzle_json(file)
    assert excinfo.type == KeyError


@pytest.mark.parametrize("test_input", ["test.png"])
def test_upload_image(fake_storage, test_data_dir, backend, test_input):
    with open(test_data_dir.joinpath(test_input), "rb") as local_file:
        local_content = local_file.read()
    file = FileStorage(open(test_data_dir.joinpath(test_input), "rb"), name=test_input)
    fake_storage.upload_image(file)
    fb: FakeBucket = backend.get_bucket("jhb-crossword")
    uploaded_content = pop_latest_item_content(fb)
    assert local_content == uploaded_content


def test_download_image(fake_storage, backend, test_data_dir):
    fname = "test.png"
    with open(test_data_dir.joinpath(fname), "rb") as file:
        uploaded_bytes = file.read()
        file.seek(0)
        backend.put_object("jhb-crossword", key_name=fname, value=file.read())
    downloaded_bytes = fake_storage.download_image(fname)
    assert downloaded_bytes.read() == uploaded_bytes


def test_download_json(fake_storage, backend, test_data_dir):
    fname = "test.json"
    with open(test_data_dir.joinpath(fname), "rb") as file:
        uploaded_bytes = file.read()
        file.seek(0)
        backend.put_object("jhb-crossword", key_name=fname, value=file.read())
    downloaded_bytes = fake_storage.download_puzzle_json(fname)
    assert downloaded_bytes.read() == uploaded_bytes


# Can't version control this large image, maybe there's a better way to test this.
# @pytest.mark.parametrize("test_input", ["large_image.png"])
# def test_upload_big_image(fake_storage, test_data_dir, test_input):
#     file = FileStorage(
#       open(test_data_dir.joinpath(test_input), "rb"), name=test_input
#       )
#     with pytest.raises(ValueError):
#         fake_storage.upload_image(file)
