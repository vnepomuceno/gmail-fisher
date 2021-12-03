from gmail_fisher.gmail_gateway import GmailGateway


def gmail_save_attachments(sender_email, keywords):
    messages = GmailGateway.run_batch_get_message_detail(sender_email, keywords, 1000)
    GmailGateway.run_batch_save_pdf_attachments(messages)
