import concurrent
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Iterable

from gmail_fisher.config import THREAD_POOL_MAX_WORKERS, OUTPUT_PATH
from gmail_fisher.data.models import GmailMessage
from gmail_fisher.gateway import GmailGateway
from gmail_fisher.utils import FileUtils

logger = logging.getLogger(__name__)


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
