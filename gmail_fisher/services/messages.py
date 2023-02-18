import logging

from gmail_fisher.utils.config import (
    LIST_MESSAGES_MAX_RESULTS,
)
from gmail_fisher.api.gateway import GmailGateway

logger = logging.getLogger(__name__)


def list_email_messages(sender_email: str, keywords: str):
    logger.info(f"Listing email messages with {sender_email=}, {keywords=}")
    GmailGateway.get_email_messages(
        sender_emails=sender_email,
        keywords=keywords,
        max_results=LIST_MESSAGES_MAX_RESULTS,
    )
