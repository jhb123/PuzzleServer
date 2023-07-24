import io

import boto3
import logging

from botocore.client import BaseClient
from botocore.exceptions import ClientError
from werkzeug.datastructures import FileStorage

logger = logging.getLogger(__name__)


class CloudStorage:

    def __init__(self):

        self.client = boto3.client('s3')
        self.bucket_name = "jhb-crossword"

    def _upload_file(self, file: FileStorage) -> bool:

        logger.info(f"uploading {file.filename}")
        try:

            memory_file = io.BytesIO(file.read())
            logger.info(f"created file in memory: {file.name}")

            response = self.client.upload_fileobj(memory_file, self.bucket_name, file.filename)

        except ClientError as e:
            logger.error(e)
            return False
        return True

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
        # If for some reason I want to change how images and
        # files are uploaded e.g. different buckets, then
        # this may make the change less difficult to make.
        return self._upload_file(file)

    def upload_puzzle_json(self, file: FileStorage):
        # ditto
        return self._upload_file(file)

    def download_image(self, file_name: str) -> io.BytesIO:
        # ditto
        return self._download_file(file_name)

    def download_puzzle_json(self, file_name: str) -> io.BytesIO:
        # ditto
        return self._download_file(file_name)


    # def upload_puzzle_json(file_name, bucket, object_name=None):
    #     """Upload a file to an S3 bucket
    #
    #     :param file_name: File to upload
    #     :param bucket: Bucket to upload to
    #     :param object_name: S3 object name. If not specified then file_name is used
    #     :return: True if file was uploaded, else False
    #     """
    #
    #     # If S3 object_name was not specified, use file_name
    #     if object_name is None:
    #         object_name = os.path.basename(file_name)
    #
    #     # Upload the file
    #     s3_client = boto3.client('s3')
    #     try:
    #         response = s3_client.upload_file(file_name, bucket, object_name)
    #     except ClientError as e:
    #         logging.error(e)
    #         return False
    #     return True
