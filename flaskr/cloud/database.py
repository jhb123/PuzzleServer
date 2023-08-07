import logging
import boto3
from botocore.exceptions import ClientError
from mypy_boto3_dynamodb import DynamoDBServiceResource
from mypy_boto3_dynamodb.service_resource import Table

from flaskr.file_validation import get_file_extension

logger = logging.getLogger(__name__)


class UserDatabase:
    def __init__(self):
        self.dynamodb: DynamoDBServiceResource = boto3.resource("dynamodb")
        self.user_table: Table = self.dynamodb.Table("crossword-userdata")
        self.email_table: Table = self.dynamodb.Table("crossword-emails")
        self.username_table: Table = self.dynamodb.Table("crossword-usernames")

    def _check_username_registered(self, username: str):
        logger.info("Checking if username is registered")
        response = self.username_table.get_item(Key={"username": username})
        logger.info(f"username is registered: {'Item' in response}")
        return "Item" in response

    def _check_email_registered(self, email: str):
        logger.info("Checking if email is registered")
        response = self.email_table.get_item(Key={"email": email})
        logger.info(f"email is registered: {'Item' in response}")
        return "Item" in response

    def get_id_for_username(self, username):
        logger.info("getting id for username")
        response = self.username_table.get_item(Key={"username": username})
        return response

    def get_id_for_email(self, email):
        logger.info("getting id for email")
        response = self.email_table.get_item(Key={"email": email})
        return response

    def get_user_data(self, user_id):
        logger.info("getting user data")
        response = self.user_table.get_item(Key={"id": user_id})
        return response

    def update_password(self, user_id, password, reset_guid):
        logger.info("updating password")
        response = self.user_table.update_item(
            Key={"id": user_id},
            UpdateExpression="set password=:p, resetGuid=:g",
            ExpressionAttributeValues={":p": password, ":g": reset_guid},
            ReturnValues="UPDATED_NEW",
        )

        return response

    def delete_email(self, email):
        self.email_table.delete_item(Key={"email": email})

    # TODO: make this simpler
    # flake8: noqa: C901
    def register_new_user(self, user_id, username: str, password, email, reset_guid):
        # self.table.

        # do a get item for username
        # do a get item for email
        try:
            email_already_used = self._check_email_registered(email)
        except ClientError:
            logger.exception()
            return False

        try:
            user_already_used = self._check_username_registered(username)
        except ClientError:
            logger.exception()
            return False

        if email_already_used or user_already_used:
            return False

        try:
            response = self.username_table.put_item(
                Item={"username": username, "id": user_id}
            )
            match response["ResponseMetadata"]["HTTPStatusCode"]:
                case 200:
                    username_set = True
                case _:
                    username_set = False
        except ClientError:
            logger.exception()
            return False

        try:
            response = self.email_table.put_item(Item={"email": email, "id": user_id})
            match response["ResponseMetadata"]["HTTPStatusCode"]:
                case 200:
                    email_set = True
                case _:
                    self.username_table.delete_item(Key={"username": username})
                    email_set = False
        except ClientError:
            logger.exception()
            self.username_table.delete_item(Key={"username": username})
            return False

        if not username_set or not email_set:
            return False

        try:
            response = self.user_table.put_item(
                Item={
                    "id": user_id,
                    "username": username,
                    "password": password,
                    "email": email,
                    "resetGuid": reset_guid,
                }
            )
            match response["ResponseMetadata"]["HTTPStatusCode"]:
                case 200:
                    return True
                case _:
                    self.username_table.delete_item(Key={"username": username})
                    self.email_table.delete_item(Key={"email": email})
                    return False
        except ClientError:
            logger.exception("There was a client error")
            return False


class PuzzleDatabase:
    def __init__(self):
        self.dynamodb: DynamoDBServiceResource = boto3.resource("dynamodb")
        self.table: Table = self.dynamodb.Table("crosswords")

    def get_puzzle_meta_data(self, puzzle_id: str):
        logger.info(f"Searching database for {puzzle_id}")
        response = self.table.get_item(Key={"id": puzzle_id})

        return response["Item"]

    def upload_puzzle_meta_data(
        self,
        puzzle_id: str,
        puzzle_json_fname: str,
        time_created: str,
        last_modified: str,
        puzzle_image_fname: str,
    ):
        if not isinstance(puzzle_id, str):
            raise TypeError("puzzle_id must be a string")
        if not isinstance(time_created, str):
            raise TypeError("time_created must be a string")
        if not isinstance(last_modified, str):
            raise TypeError("last_modified must be a string")
        if get_file_extension(puzzle_json_fname) != "json":
            raise ValueError("puzzle must be a JSON file")
        if get_file_extension(puzzle_image_fname) != "png":
            raise ValueError("puzzle icon must be a PNG file")
        self.table.put_item(
            Item={
                "id": puzzle_id,
                "puzzle": puzzle_json_fname,
                "icon": puzzle_image_fname,
                "timeCreated": time_created,
                "lastModified": last_modified,
            }
        )
