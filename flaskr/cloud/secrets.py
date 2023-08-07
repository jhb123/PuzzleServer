import logging
import boto3
from mypy_boto3_dynamodb import DynamoDBServiceResource
from mypy_boto3_dynamodb.service_resource import Table

logger = logging.getLogger(__name__)


class Secrets:
    def __init__(self):
        dynamodb: DynamoDBServiceResource = boto3.resource("dynamodb")
        self.secret_table: Table = dynamodb.Table("crossword-secrets")

    def get_secret(self, secret_name: str):
        response = self.secret_table.get_item(Key={"secret-name": secret_name})
        return response["Item"]["secret-value"]
