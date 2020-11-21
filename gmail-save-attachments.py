from __future__ import print_function

import base64
import os.path
import pickle
import re
import sys

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
DOWNLOAD_PDF_FLAG = '--download-pdf'


def gmail_save_attachments():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    args = get_arguments()
    credentials = authenticate_gmail_api()

    service = build('gmail', 'v1', credentials=credentials)
    message_results = service.users().messages() \
        .list(userId='me', q=f"from:{args['sender_emails']} {args['keywords']}").execute()

    for message in message_results['messages']:
        message = service.users().messages() \
            .get(id=message['id'], userId="me").execute()
        attachment_id = service.users().messages() \
            .get(id=message['id'], userId="me").execute()['payload']['parts'][1]['body']['attachmentId']
        print(f"[ID:{message['id']}] --> Subject: {message['snippet']}")

        if args['download']:
            attachment_base64 = service.users().messages().attachments().get(userId='me', messageId=message['id'],
                                                                             id=attachment_id).execute()['data']
            save_base64_pdf(attachment_base64, get_payslip_filename(message['snippet']), message['id'])


def authenticate_gmail_api():
    credentials = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            credentials = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(credentials, token)
    return credentials


def get_payslip_filename(subject):
    match = re.search("[1-9]?[0-9][-][1-9][0-9][0-9][0-9]", subject).group(0)
    date = f"{match.split('-')[1]}-{match.split('-')[0]}"
    return f"PaySlip_{date}.pdf"


def save_base64_pdf(base64_string, file_name, message_id):
    file_data = base64.urlsafe_b64decode(base64_string.encode('UTF-8'))
    file_handle = open(f"output/{file_name}", 'wb')
    file_handle.write(file_data)
    file_handle.close()
    print(f"[ID:{message_id}] --> Successfully saved attachment '{file_name}' ✅")
    print("----------------------------------------")


def get_arguments():
    try:
        sender_emails = sys.argv[1].strip('\'')
        keywords = sys.argv[2].strip('\'')
        if sys.argv[3] == DOWNLOAD_PDF_FLAG:
            download = bool(1)
        else:
            download = bool(0)
    except IndexError:
        download = bool(0)

    print(f"Download attachments flag {DOWNLOAD_PDF_FLAG}={download} 💾")
    return dict(sender_emails=sender_emails, keywords=keywords, download=download)


if __name__ == '__main__':
    gmail_save_attachments()
