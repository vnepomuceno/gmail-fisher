import datetime
import os
import pickle
import re
import sys
from dataclasses import dataclass

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
CREDENTIALS_FILEPATH = 'gmail_fisher/credentials.json'
TOKEN_PICKLE_FILEPATH = 'token.pickle'


@dataclass
class GmailMessage:
    id: str
    subject: str
    user_id: str
    date: datetime

    def get_total_payed_from_subject(self) -> float:
        try:
            match = re.search("[€][1-9]?[0-9].[0-9][0-9]", self.subject).group(0)
        except AttributeError:
            print(f"⚠️  Could not match total payed (e.g. €12.30) for message id='{self.id}'")
            return 0
        return float(match.strip('€'))

    def ignore_message(self) -> bool:
        if 'Refund' in self.subject or self.get_total_payed_from_subject() == 0:
            return True
        else:
            return False


def authenticate_gmail_api() -> Credentials:
    credentials = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(TOKEN_PICKLE_FILEPATH):
        with open(TOKEN_PICKLE_FILEPATH, 'rb') as token:
            credentials = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILEPATH, SCOPES)
            credentials = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(TOKEN_PICKLE_FILEPATH, 'wb') as token:
            pickle.dump(credentials, token)
    return credentials


def get_gmail_filtered_messages(credentials, sender_emails, keywords, max_results) -> list:
    service = build('gmail', 'v1', credentials=credentials)

    list_message_results = service.users().messages().list(
        userId='me',
        q=f"from:{sender_emails} {keywords}",
        maxResults=max_results
    ).execute()

    if list_message_results['resultSizeEstimate'] == 0:
        print('No messages found.')
        sys.exit(0)

    message_list = list()
    for message in list_message_results['messages']:
        get_message_result = service.users().messages().get(id=message['id'], userId="me").execute()
        message = GmailMessage(
            id=message['id'],
            subject=get_message_result['snippet'],
            user_id='me',
            date=get_date(
                next(item for item in get_message_result['payload']['headers'] if item["name"] == "Date")['value']
            )
        )
        print(f"Fetched message from date='{message.date.strftime('%Y-%m-%d')}', "
              f"subject='{message.subject[0:120]} ...'")
        message_list.append(message)

    return message_list


def get_date(date_str) -> datetime:
    """
    Receives a string date in the format 'Sun, 29 Nov 2020 21:32:07 +0000 (UTC)',
    and returns a datetime with precision up to the day.
    """
    date_arr = date_str.strip(' +0000 (UTC)').split(', ')[1].split(' ')
    date_str = f"{date_arr[0]} {date_arr[1]} {date_arr[2]}"

    try:
        return datetime.datetime.strptime(date_str, '%d %b %Y')
    except ValueError as ve:
        print(f"⚠️  Date could not be parsed '{date_str}'. Raised error {ve}")
        return datetime.datetime.now()
