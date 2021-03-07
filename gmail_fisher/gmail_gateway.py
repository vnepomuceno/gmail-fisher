import logging
import os
import pickle
from typing import List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from .models import GmailMessage, MessageAttachment

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


class GmailGateway:
    @classmethod
    def __list_message_ids(
        cls, sender_emails: str, keywords: str, max_results: int
    ) -> List[str]:
        """
        For a given sender email and comma-separated keywords, retrieve the matching
        message IDs and return them as a list.
        """
        list_message_results = (
            GmailClient.get_instance()
            .users()
            .messages()
            .list(
                userId="me",
                q=f"from:{sender_emails} {keywords}",
                maxResults=max_results,
            )
            .execute()
        )

        if list_message_results["resultSizeEstimate"] == 0:
            logging.warning(
                f"No messages found for email='{sender_emails}', keywords='{keywords}'"
            )
            return []
        else:
            message_ids = [
                message["id"] for message in list_message_results["messages"]
            ]
            logging.info(f"Found {len(message_ids)} message IDs {message_ids}")
            return message_ids

    @classmethod
    def __get_message_detail(cls, message_id: str) -> GmailMessage:
        """
        Fetches the detail of a message with a given message ID.
        """
        get_message_result = (
            GmailClient.get_instance()
            .users()
            .messages()
            .get(id=message_id, userId="me")
            .execute()
        )

        attachment_list = list()
        if get_message_result["payload"].keys().__contains__("parts"):
            for part in get_message_result["payload"]["parts"]:
                if part["mimeType"] in ["application/pdf", "application/octet-stream"]:
                    attachment = MessageAttachment(
                        part_id=part["partId"],
                        filename=part["filename"],
                        id=part["body"]["attachmentId"],
                    )
                    attachment_list.append(attachment)

        message = GmailMessage(
            id=message_id,
            subject=get_message_result["snippet"],
            user_id="me",
            date=next(
                item
                for item in get_message_result["payload"]["headers"]
                if item["name"] == "Date"
            )["value"],
            attachments=attachment_list,
        )
        logging.info(f"Fetched message {message}")
        return message

    @classmethod
    def get_filtered_messages(
        cls, sender_emails: str, keywords: str, max_results: int
    ) -> List[GmailMessage]:
        """
        For a given sender email and comma-separated keywords, retrieve the matching
        messages and corresponding detailed metadata and returns a list of
        `GmailMessage` objects.
        """
        message_ids = cls.__list_message_ids(sender_emails, keywords, max_results)
        return [cls.__get_message_detail(message_id) for message_id in message_ids]

    @classmethod
    def get_message_attachment(cls, message_id: str, attachment_id: str) -> str:
        """
        Returns a base-64 string with the content for the .pdf attachment with 'message_id'
        and 'attachment_id'.
        """
        return (
            GmailClient.get_instance()
            .users()
            .messages()
            .attachments()
            .get(userId="me", messageId=message_id, id=attachment_id)
            .execute()["data"]
        )
