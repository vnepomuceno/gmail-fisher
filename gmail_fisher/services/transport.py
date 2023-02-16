import logging
from pathlib import Path

from gmail_fisher.data.models import TransportServiceType
from gmail_fisher.data.s3_uploader import S3BucketUploader
from gmail_fisher.parsers.transportation import TransportationExpenseParser, BoltParser

logger = logging.getLogger(__name__)


def export_transport_expenses(
    service_type: TransportServiceType, output_path: Path, upload_s3: bool = False
):
    logger.info(
        f"Exporting transportation expenses with {service_type=}, {output_path=}"
    )
    if service_type is TransportServiceType.BOLT:
        TransportationExpenseParser.serialize_expenses_to_json_file(
            expenses=BoltParser.fetch_expenses(), output_path=str(output_path)
        )
    else:
        raise RuntimeError(f"Invalid transport service type {service_type=}")

    if upload_s3:
        S3BucketUploader().upload(filepath=output_path, key=output_path.name)
