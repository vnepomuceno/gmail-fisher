import os
import pickle
import sys
from typing import List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from .models import GmailMessage, MessageAttachment
from .log import success, info

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
CREDENTIALS_FILEPATH = "gmail_fisher/credentials.json"
TOKEN_PICKLE_FILEPATH = "token.pickle"


class GmailClient:
    __instance = None

    @classmethod
    def get_instance(cls):
        if not cls.__instance:
            credentials = cls.__authenticate()
            cls.__instance = build("gmail", "v1", credentials=credentials)
        return cls.__instance

    @classmethod
    def __authenticate(cls) -> Credentials:
        credentials = None
        if os.path.exists(TOKEN_PICKLE_FILEPATH):
            with open(TOKEN_PICKLE_FILEPATH, "rb") as token:
                credentials = pickle.load(token)
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_FILEPATH, SCOPES
                )
                credentials = flow.run_local_server(port=0)
            with open(TOKEN_PICKLE_FILEPATH, "wb") as token:
                pickle.dump(credentials, token)
        return credentials


def get_filtered_messages(
    sender_emails, keywords, max_results, get_attachments
) -> List[GmailMessage]:
    client = GmailClient.get_instance()
    list_message_results = (
        client.users()
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
            client.users().messages().get(id=message["id"], userId="me").execute()
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


def get_message_attachment(message_id, attachment_id) -> str:
    """
    Returns a base-64 string with the content for the .pdf attachment with 'message_id'
    and 'attachment_id'.
    """
    client = GmailClient.get_instance()
    return (
        client.users()
        .messages()
        .attachments()
        .get(userId="me", messageId=message_id, id=attachment_id)
        .execute()["data"]
    )
