import datetime
import os
import pickle
import re
import sys
from dataclasses import dataclass
from typing import List

from .log import success, info, warning
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
CREDENTIALS_FILEPATH = "gmail_fisher/credentials.json"
TOKEN_PICKLE_FILEPATH = "token.pickle"


@dataclass
class MessageAttachment:
    part_id: str
    filename: str
    id: str


@dataclass
class GmailMessage:
    id: str
    subject: str
    user_id: str
    date: datetime
    attachments: List[MessageAttachment]

    def get_total_payed_from_subject(self) -> float:
        """
        Fetches message subject in format e.g. '... €15.40 ...' and returns
        a float equivalent to the total payed, or 0 if there is not match.
        """
        try:
            match = re.search("[€][1-9]?[0-9].[0-9][0-9]", self.subject).group(0)
        except AttributeError:
            warning(
                "Could not match total payed (e.g. €12.30)", {"message_id": self.id}
            )

            return 0
        return float(match.strip("€"))

    def get_date_as_datetime(self) -> datetime:
        """
        Fetches message date in the format e.g. 'Sun, 29 Nov 2020 21:32:07 +0000 (UTC)',
        and returns a datetime with precision up to the day.
        """
        date_arr = self.date.strip(" +0000 (UTC)").split(", ")[1].split(" ")
        date_str = f"{date_arr[0]} {date_arr[1]} {date_arr[2]}"

        try:
            return datetime.datetime.strptime(date_str, "%d %b %Y")
        except ValueError as ve:
            warning("Date could not be parsed", {"date": date_str, "error": ve})
            return datetime.datetime.now()

    def ignore_message(self) -> bool:
        """
        Fetches message subject and returns True if it contains the word 'Refund' or
        if there is no total payed matched in that subject, or False otherwise.
        """
        if "Refund" in self.subject or self.get_total_payed_from_subject() == 0:
            return True
        else:
            return False


def authenticate() -> Credentials:
    credentials = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(TOKEN_PICKLE_FILEPATH):
        with open(TOKEN_PICKLE_FILEPATH, "rb") as token:
            credentials = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILEPATH, SCOPES
            )
            credentials = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(TOKEN_PICKLE_FILEPATH, "wb") as token:
            pickle.dump(credentials, token)
    return credentials


def get_filtered_messages(
    credentials, sender_emails, keywords, max_results, get_attachments
) -> List[GmailMessage]:
    service = build("gmail", "v1", credentials=credentials)
    list_message_results = (
        service.users()
        .messages()
        .list(userId="me", q=f"from:{sender_emails} {keywords}", maxResults=max_results)
        .execute()
    )

    if list_message_results["resultSizeEstimate"] == 0:
        info("No messages found")
        sys.exit(0)

    message_list = list()
    for message in list_message_results["messages"]:
        get_message_result = (
            service.users().messages().get(id=message["id"], userId="me").execute()
        )

        attachment_list = list()
        if get_attachments and get_message_result["payload"].keys().__contains__(
            "parts"
        ):
            for part in get_message_result["payload"]["parts"]:
                if part["mimeType"] in ["application/pdf", "application/octet-stream"]:
                    attachment = MessageAttachment(
                        part_id=part["partId"],
                        filename=part["filename"],
                        id=part["body"]["attachmentId"],
                    )
                    success("Attachment detected", {"attachment": attachment})
                    attachment_list.append(attachment)

        message = GmailMessage(
            id=message["id"],
            subject=get_message_result["snippet"],
            user_id="me",
            date=next(
                item
                for item in get_message_result["payload"]["headers"]
                if item["name"] == "Date"
            )["value"],
            attachments=attachment_list,
        )
        success("Fetched message", {"message": message})
        message_list.append(message)

    return message_list


def get_message_attachment(credentials, message_id, attachment_id) -> str:
    """
    Returns a base-64 string with the content for the .pdf attachment with 'message_id'
    and 'attachment_id'.
    """
    service = build("gmail", "v1", credentials=credentials)
    return (
        service.users()
        .messages()
        .attachments()
        .get(userId="me", messageId=message_id, id=attachment_id)
        .execute()["data"]
    )
