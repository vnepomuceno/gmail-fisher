from pathlib import Path

from gmail_fisher.data.s3_uploader import S3BucketUploader
from gmail_fisher.parsers.bank import BancoCttParser


def export_bank_expenses(output_filepath: Path, upload_s3: bool = False):
    expenses = BancoCttParser.fetch_expenses()
    BancoCttParser.serialize_expenses_to_json_file(expenses, output_filepath)

    if upload_s3:
        S3BucketUploader().upload(filepath=output_filepath, key=output_filepath.name)
