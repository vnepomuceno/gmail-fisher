import concurrent
import logging
from concurrent.futures.thread import ThreadPoolExecutor
from pathlib import Path
from typing import Iterable

from gmail_fisher.config import (
    THREAD_POOL_MAX_WORKERS,
    LIST_MESSAGES_MAX_RESULTS,
    OUTPUT_PATH,
)
from gmail_fisher.gateway import GmailGateway
from gmail_fisher.models import (
    GmailMessage,
    FoodServiceType,
    TransportServiceType,
    FoodExpense,
)
from gmail_fisher.parsers.bank import BancoCttParser
from gmail_fisher.parsers.food import UberEatsParser, FoodExpenseParser, BoltFoodParser
from gmail_fisher.parsers.transportation import TransportationExpenseParser, BoltParser
from gmail_fisher.s3_uploader import S3BucketUploader
from gmail_fisher.utils import FileUtils

logger = logging.getLogger(__name__)


def list_email_messages(sender_email: str, keywords: str):
    logger.info(f"Listing email messages with {sender_email=}, {keywords=}")
    GmailGateway.get_email_messages(
        sender_emails=sender_email,
        keywords=keywords,
        max_results=LIST_MESSAGES_MAX_RESULTS,
    )


def get_food_expenses() -> Iterable[FoodExpense]:
    return list(BoltFoodParser.fetch_expenses()) + list(UberEatsParser.fetch_expenses())


def export_food_expenses(
    service_type: FoodServiceType, output_path: Path, upload_s3: bool = False
):
    logger.info(f"Exporting food expenses with {service_type=}, {output_path=}")

    if service_type is FoodServiceType.UBER_EATS:
        FoodExpenseParser.serialize_expenses_to_json_file(
            expenses=UberEatsParser.fetch_expenses(), output_path=str(output_path)
        )
    elif service_type is FoodServiceType.BOLT_FOOD:
        FoodExpenseParser.serialize_expenses_to_json_file(
            expenses=BoltFoodParser.fetch_expenses(), output_path=str(output_path)
        )
    elif service_type is FoodServiceType.ALL:
        FoodExpenseParser.serialize_expenses_to_json_file(
            expenses=list(BoltFoodParser.fetch_expenses())
            + list(UberEatsParser.fetch_expenses()),
            output_path=str(output_path),
        )
    else:
        raise RuntimeError(f"Invalid food service type {service_type=}")

    if upload_s3:
        S3BucketUploader().upload(filepath=output_path, key=output_path.name)


def export_bank_expenses(output_filepath: Path, upload_s3: bool = False):
    expenses = BancoCttParser.fetch_expenses()
    BancoCttParser.serialize_expenses_to_json_file(expenses, output_filepath)

    if upload_s3:
        S3BucketUploader().upload(filepath=output_filepath, key=output_filepath.name)


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


def export_email_attachments(sender_email: str, keywords: str):
    logger.info(f"Exporting email attachments with {sender_email=}, {keywords=}")
    messages = GmailGateway.get_email_messages(sender_email, keywords, 1000)
    __export_pdf_attachments(messages)


def __export_pdf_attachments(messages: Iterable[GmailMessage]):
    with ThreadPoolExecutor(max_workers=THREAD_POOL_MAX_WORKERS) as pool:
        future_mappings = {}
        for message in messages:
            for attachment in message.attachments:
                future = pool.submit(
                    GmailGateway.get_message_attachment,
                    message.id,
                    attachment.id,
                )
                future_mappings[future] = (message.id, message.subject)

        for future in concurrent.futures.as_completed(future_mappings.keys()):
            try:
                base64_content = future.result()
                message_id, message_subject = future_mappings[future]
                FileUtils.save_base64_pdf(
                    base64_string=base64_content,
                    file_path=OUTPUT_PATH
                    / FileUtils.get_payslip_filename(message_subject),
                    message_id=message_id,
                )
            except Exception as ex:
                logger.error(f"Error fetching future result {ex}")
