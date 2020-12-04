from __future__ import print_function

print('__file__={0:<35} | __name__={1:<20} | __package__={2:<20}'.format(__file__, __name__, str(__package__)))
import base64
import re
import sys
from .authenticate import authenticate_gmail_api
from googleapiclient.discovery import build

DOWNLOAD_PDF_FLAG = '--download-pdf'


def gmail_save_attachments(argv):
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    args = get_arguments(argv)
    credentials = authenticate_gmail_api()

    service = build('gmail', 'v1', credentials=credentials)
    message_results = service.users().messages() \
        .list(userId='me', q=f"from:{args['sender_emails']} {args['keywords']}").execute()

    if message_results['resultSizeEstimate'] == 0:
        print("No messages found for provided arguments. Goodbye")
        sys.exit(0)

    for message in message_results['messages']:
        message = service.users().messages() \
            .get(id=message['id'], userId="me").execute()
        print(f"[ID:{message['id']}] --> Subject: {message['snippet']}")

        if args['download']:
            attachment_id = service.users().messages() \
                .get(id=message['id'], userId="me").execute()['payload']['parts'][1]['body']['attachmentId']
            attachment_base64 = service.users().messages().attachments().get(userId='me', messageId=message['id'],
                                                                             id=attachment_id).execute()['data']
            save_base64_pdf(attachment_base64, get_payslip_filename(message['snippet']), message['id'])


def get_payslip_filename(subject: str) -> str:
    match = re.search("[1-9]?[0-9][-][1-9][0-9][0-9][0-9]", subject).group(0)
    date = f"{match.split('-')[1]}-{match.split('-')[0]}"
    return f"PaySlip_{date}.pdf"


def save_base64_pdf(base64_string: str, file_name: str, message_id: str):
    file_data = base64.urlsafe_b64decode(base64_string.encode('UTF-8'))
    file_handle = open(f"output/{file_name}", 'wb')
    file_handle.write(file_data)
    file_handle.close()
    print(f"[ID:{message_id}] --> Successfully saved attachment '{file_name}' ✅")
    print("----------------------------------------")


def get_arguments(argv) -> dict:
    try:
        sender_emails = argv[2].strip('\'')
        keywords = argv[3].strip('\'')
        if argv[3] == DOWNLOAD_PDF_FLAG:
            download = bool(1)
        else:
            download = bool(0)
    except IndexError:
        download = bool(0)

    print(f"Download attachments flag {DOWNLOAD_PDF_FLAG}={download} 💾")
    return dict(sender_emails=sender_emails, keywords=keywords, download=download)