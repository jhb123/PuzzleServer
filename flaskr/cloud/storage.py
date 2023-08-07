import io
import json

import boto3
import logging

from botocore.exceptions import ClientError
from mypy_boto3_s3 import S3Client
from werkzeug.datastructures import FileStorage

from flaskr.file_validation import check_puzzle_json, get_file_extension

logger = logging.getLogger(__name__)


class CloudStorage:
    max_thumbnail_size = 20000

    def __init__(self):
        self.client: S3Client = boto3.client("s3")
        self.bucket_name = "jhb-crossword"

    def _upload_file(self, file: FileStorage):
        if file is None:
            raise ValueError("file cannot be None")
        logger.info(f"uploading {file.filename}")
        try:
            memory_file = io.BytesIO(file.read())
            logger.info(f"created file in memory: {file.filename}")

            self.client.upload_fileobj(memory_file, self.bucket_name, file.filename)

        except ClientError as e:
            logger.error(e)

    def _download_file(self, file_name: str) -> io.BytesIO:
        logger.info(f"downloading {file_name}")
        memory_file = io.BytesIO()
        try:
            # with memory_file as f:
            self.client.download_fileobj(self.bucket_name, file_name, memory_file)
            # memory_file.seek(0)
        except ClientError as e:
            logger.error(e)
            raise

        memory_file.seek(0)
        return memory_file

    def upload_image(self, file: FileStorage):
        if file is None:
            raise ValueError("file cannot be None")
        file_type = get_file_extension(file.filename)
        if file_type != "png":
            raise ValueError(f"Expected png, got {file_type}")

        file_bytes = file.stream.read()
        if len(file_bytes) > self.max_thumbnail_size:
            raise ValueError(
                f"Thumbnail ({len(file_bytes)}) exceeds maximum "
                f"upload size ({self.max_thumbnail_size})"
            )
        file.stream.seek(0)
        return self._upload_file(file)

    def upload_puzzle_json(self, file: FileStorage):
        if file is None:
            raise ValueError("file cannot be None")
        file_type = get_file_extension(file.filename)
        if file_type != "json":
            raise ValueError(f"Expected json file, got {file_type}")

        # check the content matches the expected json format
        file_bytes = file.stream.read()
        file_string = file_bytes.decode("UTF-8")
        check_puzzle_json(json.loads(file_string))
        file.stream.seek(0)

        return self._upload_file(file)

    def download_image(self, file_name: str) -> io.BytesIO:
        file_type = get_file_extension(file_name)
        if file_type != "png":
            raise ValueError(f"Expected png file, got {file_type}")
        return self._download_file(file_name)

    def download_puzzle_json(self, file_name: str) -> io.BytesIO:
        file_type = get_file_extension(file_name)
        if file_type != "json":
            raise ValueError(f"Expected json file, got {file_type}")
        return self._download_file(file_name)
