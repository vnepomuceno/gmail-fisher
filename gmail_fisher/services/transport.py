import logging
from pathlib import Path

from gmail_fisher.data.s3_uploader import S3BucketUploader
from gmail_fisher.parsers.transportation import (
    TransportationExpenseParser,
    BoltParser,
    UberParser,
)

logger = logging.getLogger(__name__)


def export_transport_expenses(output_path: Path, upload_s3: bool = False):
    logger.info(f"Exporting transportation expenses with {output_path=}")

    transport_expenses = list(
        BoltParser.fetch_expenses() + list(UberParser.fetch_expenses())
    )
    TransportationExpenseParser.serialize_expenses_to_json_file(
        expenses=transport_expenses, output_path=str(output_path)
    )

    if upload_s3:
        S3BucketUploader().upload(filepath=output_path, key=output_path.name)
