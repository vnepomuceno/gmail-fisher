import base64
import concurrent
import os
from concurrent.futures.thread import ThreadPoolExecutor
from pathlib import Path
from typing import Iterable, Final, List

import google_auth_httplib2
import httplib2
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource

from gmail_fisher.config import (
    AUTH_PATH,
    GMAIL_READ_ONLY_SCOPE,
    THREAD_POOL_MAX_WORKERS,
)
from gmail_fisher.models import GmailMessage, MessageAttachment
from gmail_fisher.utils import get_logger

logger = get_logger(__name__)


class GmailClient:
    scopes: List[str] = [GMAIL_READ_ONLY_SCOPE]
    credentials_path: Final[Path] = AUTH_PATH / "credentials.json"
    token_json_path: Final[Path] = AUTH_PATH / "auth_token.json"
    __instance: Resource = None

    @classmethod
    def auth_http_request(cls) -> google_auth_httplib2.AuthorizedHttp:
        return google_auth_httplib2.AuthorizedHttp(
            cls.__authenticate(), http=httplib2.Http()
        )

    @classmethod
    def get_instance(cls) -> Resource:
        if not cls.__instance:
            credentials = cls.__authenticate()
            cls.__instance = build("gmail", "v1", credentials=credentials)
        return cls.__instance

    @classmethod
    def __authenticate(cls) -> Credentials:
        credentials = None
        if os.path.exists(cls.token_json_path):
            with open(cls.token_json_path, "rb") as token:
                credentials = Credentials.from_authorized_user_file(
                    str(cls.token_json_path), cls.scopes
                )
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(cls.credentials_path), cls.scopes
                )
                credentials = flow.run_local_server(port=0)
            with open(cls.token_json_path, "w") as token:
                token.write(credentials.to_json())
        return credentials


class GmailGateway:
    """Maximum number of workers for thread pool executor"""

    @classmethod
    def list_message_ids(
        cls, sender_emails: str, keywords: str, max_results: int
    ) -> Iterable[str]:
        """
        For a given sender email and comma-separated keywords, retrieve the matching
        message IDs and return them as a list.
        """
        logger.info(f"Fetching emails with {sender_emails=}, {keywords=}")
        list_message_results = (
            GmailClient.get_instance()
            .users()
            .messages()
            .list(
                userId="me",
                q=f"from:{sender_emails} {keywords}",
                maxResults=max_results,
            )
            .execute(http=GmailClient.auth_http_request())
        )

        if list_message_results["resultSizeEstimate"] == 0:
            logger.warning(
                f"No messages found for email='{sender_emails}', keywords='{keywords}'"
            )
            return []
        else:
            message_ids = [
                message["id"] for message in list_message_results["messages"]
            ]
            logger.info(
                f"Found {len(message_ids)} emails for {sender_emails=}, {keywords=}"
            )
            return message_ids

    @classmethod
    def get_email_messages(
        cls,
        sender_emails: str,
        keywords: str,
        max_results: int,
        fetch_body: bool = False,
    ) -> Iterable[GmailMessage]:
        results = []
        message_ids = GmailGateway.list_message_ids(
            sender_emails, keywords, max_results
        )
        with ThreadPoolExecutor(max_workers=THREAD_POOL_MAX_WORKERS) as pool:
            logger.info(f"Submitting {len(set(message_ids))} tasks to thread pool")
            futures = [
                pool.submit(GmailGateway.get_message_detail, message_id, fetch_body)
                for message_id in message_ids
            ]

            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as ex:
                    logger.error(f"Error fetching future result {ex}")

        logger.success(
            f"TOTAL SUCCESSFUL RESULTS {len(results)} for 'run_batch_get_message_detail'"
        )

        return results

    @classmethod
    def get_message_detail(cls, message_id: str, fetch_body: bool) -> GmailMessage:
        """
        Fetches the detail of a message with a given message ID.
        """
        get_message_result = (
            GmailClient.get_instance()
            .users()
            .messages()
            .get(id=message_id, userId="me")
            .execute(http=GmailClient.auth_http_request())
        )

        attachment_list = list()
        attachment = None
        if get_message_result["payload"].keys().__contains__("parts"):
            for part in get_message_result["payload"]["parts"]:
                if part["mimeType"] in ["application/pdf", "application/octet-stream"]:
                    attachment = MessageAttachment(
                        part_id=part["partId"],
                        filename=part["filename"],
                        id=part["body"]["attachmentId"],
                    )
                elif part["mimeType"] in ["multipart/mixed"]:
                    for subpart in part["parts"]:
                        if subpart["mimeType"].__contains__("pdf"):
                            attachment = MessageAttachment(
                                part_id=subpart["partId"],
                                filename=subpart["filename"],
                                id=subpart["body"]["attachmentId"],
                            )
                if attachment:
                    attachment_list.append(attachment)

        message = GmailMessage(
            id=message_id,
            subject=get_message_result["snippet"],
            date=next(
                item
                for item in get_message_result["payload"]["headers"]
                if item["name"] == "Date"
            )["value"],
            attachments=attachment_list,
        )
        logger.success(
            f"Fetched email details for {message_id=} subject={message.subject[:120]}..."
        )

        if not fetch_body:
            return message

        try:
            if get_message_result["payload"]["body"]["size"] == 0:
                message_parts = get_message_result["payload"].get("parts", None)
                message.body = (
                    base64.urlsafe_b64decode(message_parts[0]["body"]["data"])
                    .decode("utf-8")
                    .replace("\n", "")
                )
            else:
                message.body = (
                    base64.urlsafe_b64decode(
                        get_message_result["payload"]["body"]["data"]
                    )
                    .decode("utf-8")
                    .replace("\n", "")
                )
        except Exception as e:
            logger.error(f"ERROR parsing body {e}")

        return message

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
            .execute(http=GmailClient.auth_http_request())["data"]
        )
