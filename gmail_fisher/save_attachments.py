from __future__ import print_function

import base64
import os
import re

from .gmail_gateway import authenticate
from .gmail_gateway import get_filtered_messages
from .gmail_gateway import get_message_attachment
from .log import success

DOWNLOAD_PDF_FLAG = "--download-pdf"
OUTPUT_DIRECTORY = "gmail_fisher/output/"


def gmail_save_attachments(argv):
    args = get_arguments(argv)
    credentials = authenticate()
    messages = get_filtered_messages(
        credentials, args["sender_emails"], args["keywords"], 1000, True
    )

    for message in messages:
        if args["download"]:
            for attachment in message.attachments:
                base64_content = get_message_attachment(
                    credentials, message.id, attachment.id
                )
                save_base64_pdf(
                    base64_content, get_payslip_filename(message.subject), message.id
                )


def get_payslip_filename(subject: str) -> str:
    match = re.search("[1-9]?[0-9][-][1-9][0-9][0-9][0-9]", subject).group(0)
    date = f"{match.split('-')[1]}-{match.split('-')[0]}"
    return f"PaySlip_{date}.pdf"


def save_base64_pdf(base64_string: str, file_name: str, message_id: str):
    file_data = base64.urlsafe_b64decode(base64_string.encode("UTF-8"))

    if not os.path.isdir(OUTPUT_DIRECTORY):
        os.mkdir(OUTPUT_DIRECTORY)
    file_handle = open(f"{OUTPUT_DIRECTORY}{file_name}", "wb")
    file_handle.write(file_data)
    file_handle.close()
    success(
        "Successfully saved attachment",
        {"filename": file_name, "message_id": message_id},
    )
    print("----------------------------------------")


def get_arguments(argv) -> dict:
    try:
        sender_emails = argv[2].strip("'")
        keywords = argv[3].strip("'")
        if argv[4] == DOWNLOAD_PDF_FLAG:
            download = bool(1)
        else:
            download = bool(0)
    except IndexError:
        download = bool(0)

    print(f"Download attachments flag {DOWNLOAD_PDF_FLAG}={download} 💾")
    return dict(sender_emails=sender_emails, keywords=keywords, download=download)
