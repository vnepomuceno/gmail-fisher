import base64
import concurrent
import logging
import os
import pickle
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Iterable, Final

import google_auth_httplib2
import httplib2
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource

from gmail_fisher.models import GmailMessage, MessageAttachment
from gmail_fisher.utils import FileUtils


class GmailClient:
    __SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
    __CREDENTIALS_FILEPATH = "gmail_fisher/credentials.json"
    __TOKEN_PICKLE_FILEPATH = "token.pickle"
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
        if os.path.exists(cls.__TOKEN_PICKLE_FILEPATH):
            with open(cls.__TOKEN_PICKLE_FILEPATH, "rb") as token:
                credentials = pickle.load(token)
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    cls.__CREDENTIALS_FILEPATH, cls.__SCOPES
                )
                credentials = flow.run_local_server(port=0)
            with open(cls.__TOKEN_PICKLE_FILEPATH, "wb") as token:
                pickle.dump(credentials, token)
        return credentials


class GmailGateway:
    """Maximum number of workers for thread pool executor"""

    MAX_WORKERS: Final[int] = 20

    @classmethod
    def __list_message_ids(
        cls, sender_emails: str, keywords: str, max_results: int
    ) -> Iterable[str]:
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
            .execute(http=GmailClient.auth_http_request())
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
    def __get_message_detail(cls, message_id: str, fetch_body: bool) -> GmailMessage:
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
            date=next(
                item
                for item in get_message_result["payload"]["headers"]
                if item["name"] == "Date"
            )["value"],
            attachments=attachment_list,
        )
        logging.info(f"Fetched message {message}")

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
            logging.error(f"ERROR parsing body {e}")

        return message

    @classmethod
    def run_batch_get_message_detail(
        cls,
        sender_emails: str,
        keywords: str,
        max_results: int,
        fetch_body: bool = False,
    ) -> Iterable[GmailMessage]:
        results = []
        message_ids = GmailGateway.__list_message_ids(
            sender_emails, keywords, max_results
        )
        with ThreadPoolExecutor(max_workers=cls.MAX_WORKERS) as pool:
            futures = [
                pool.submit(GmailGateway.__get_message_detail, message_id, fetch_body)
                for message_id in message_ids
            ]

            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as ex:
                    logging.error(f"Error fetching future result {ex}")

        logging.info(
            f"TOTAL SUCCESSFUL RESULTS {len(results)} for 'run_batch_get_message_detail'"
        )

        return results

    @classmethod
    def run_batch_save_pdf_attachments(cls, messages: Iterable[GmailMessage]):
        with ThreadPoolExecutor(max_workers=20) as pool:
            future_mappings = {}
            for message in messages:
                for attachment in message.attachments:
                    future = pool.submit(
                        GmailGateway.__get_message_attachment,
                        message.id,
                        attachment.id,
                    )
                    future_mappings[future] = (message.id, message.subject)

            for future in concurrent.futures.as_completed(future_mappings.keys()):
                try:
                    base64_content = future.result()
                    message_id, message_subject = future_mappings[future]
                    FileUtils.save_base64_pdf(
                        base64_content,
                        FileUtils.get_payslip_filename(message_subject),
                        message_id,
                    )
                except Exception as ex:
                    logging.error(f"Error fetching future result {ex}")

    @classmethod
    def __get_message_attachment(cls, message_id: str, attachment_id: str) -> str:
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
