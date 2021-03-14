import base64
import concurrent
import logging
import os
import pickle
import re
from concurrent.futures.thread import ThreadPoolExecutor
from typing import List, Callable, Iterable

import google_auth_httplib2
import httplib2
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource

from .models import GmailMessage, MessageAttachment

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
CREDENTIALS_FILEPATH = "gmail_fisher/credentials.json"
TOKEN_PICKLE_FILEPATH = "token.pickle"


class GmailClient:
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
    def __get_message_detail(cls, message_id: str) -> GmailMessage:
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
    def run_batch_get_message_detail(
        cls, sender_emails: str, keywords: str, max_results: int
    ) -> Iterable[GmailMessage]:
        results = []
        message_ids = GmailGateway.__list_message_ids(
            sender_emails, keywords, max_results
        )
        with ThreadPoolExecutor(max_workers=20) as pool:
            futures = [
                pool.submit(GmailGateway.__get_message_detail, message_id)
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


class FileUtils:
    __OUTPUT_DIRECTORY = "gmail_fisher/output/"

    @classmethod
    def get_payslip_filename(cls, subject: str) -> str:
        match = re.search("[1-9]?[0-9][-][1-9][0-9][0-9][0-9]", subject).group(0)
        date = f"{match.split('-')[1]}-{match.split('-')[0]}"
        return f"PaySlip_{date}.pdf"

    @classmethod
    def save_base64_pdf(cls, base64_string: str, file_name: str, message_id: str):
        file_data = base64.urlsafe_b64decode(base64_string.encode("UTF-8"))

        if not os.path.isdir(cls.__OUTPUT_DIRECTORY):
            os.mkdir(cls.__OUTPUT_DIRECTORY)
        file_handle = open(f"{cls.__OUTPUT_DIRECTORY}{file_name}", "wb")
        file_handle.write(file_data)
        file_handle.close()
        logging.info(
            f"Successfully saved attachment with filename='{file_name}' and message_id='{message_id}'"
        )
