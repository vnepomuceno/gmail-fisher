import os
from pathlib import Path

import boto3
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv

from gmail_fisher.utils import get_logger

load_dotenv()
logger = get_logger(__name__)


class S3BucketUploader:
    def __init__(self):
        access_key = os.environ.get("S3_ACCESS_KEY")
        self.bucket_name = os.environ.get("S3_BUCKET_NAME")
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=access_key,
            aws_secret_access_key=os.environ.get("S3_SECRET_KEY"),
        )
        logger.info(f"S3 client created for ACCESS_KEY='{access_key}'")
        logger.info(f"S3 bucket name is '{self.bucket_name}'")

    def upload(self, filepath: Path, key: str):
        try:
            logger.info(
                f"Uploading {filepath=} to bucket='{self.bucket_name}' with {key=}..."
            )
            self.s3_client.upload_file(str(filepath), self.bucket_name, key)
        except FileNotFoundError as fnfe:
            logger.error(
                f"File was not found for {filepath=}, exception='{fnfe.__class__.__name__}', message='{fnfe}'"
            )
        except NoCredentialsError as nce:
            logger.error(
                f"Credentials not provided, exception='{nce.__class__.__name__}', message='{nce}'"
            )

        logger.success(
            f"Successfully uploaded {filepath=} to bucket='{self.bucket_name}' with {key=}"
        )


if __name__ == "__main__":
    S3BucketUploader().upload(filepath=Path("export_expenses.sh"), key="export_expenses.sh")
