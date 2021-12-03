import logging
import concurrent
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Iterable

from gmail_fisher.config import THREAD_POOL_MAX_WORKERS
from gmail_fisher.gateway import GmailGateway
from gmail_fisher.models import GmailMessage
from gmail_fisher.utils import FileUtils

logger = logging.getLogger(__name__)


def gmail_save_attachments(sender_email, keywords):
    messages = get_email_messages(sender_email, keywords, 1000)
    export_pdf_attachments(messages)


def get_email_messages(
    sender_emails: str,
    keywords: str,
    max_results: int,
    fetch_body: bool = False,
) -> Iterable[GmailMessage]:
    results = []
    message_ids = GmailGateway.list_message_ids(sender_emails, keywords, max_results)
    with ThreadPoolExecutor(max_workers=THREAD_POOL_MAX_WORKERS) as pool:
        logger.info(f"Submitting {len(set(message_ids))} tasks to thread pool")
        futures = [
            pool.submit(GmailGateway.get_message_detail, message_id, fetch_body)
            for message_id in message_ids
        ]

        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as ex:
                logger.error(f"Error fetching future result {ex}")

    logger.info(
        f"TOTAL SUCCESSFUL RESULTS {len(results)} for 'run_batch_get_message_detail'"
    )

    return results


def export_pdf_attachments(messages: Iterable[GmailMessage]):
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
                    base64_content,
                    FileUtils.get_payslip_filename(message_subject),
                    message_id,
                )
            except Exception as ex:
                logger.error(f"Error fetching future result {ex}")
