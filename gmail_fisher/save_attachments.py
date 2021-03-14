from __future__ import print_function

from .gmail_gateway import GmailGateway

OUTPUT_DIRECTORY = "gmail_fisher/output/"


def gmail_save_attachments(sender_email, keywords):
    messages = GmailGateway.run_batch_get_message_detail(sender_email, keywords, 1000)
    GmailGateway.run_batch_save_pdf_attachments(messages)
