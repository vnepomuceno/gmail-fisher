import base64
import concurrent
import os
import time
import socket
from concurrent.futures.thread import ThreadPoolExecutor
from pathlib import Path
from typing import Iterable, Final, List, Any, Dict, Optional

import google_auth_httplib2
import httplib2
from alive_progress import alive_bar
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError

from gmail_fisher import get_logger
from gmail_fisher.utils.config import (
    AUTH_PATH,
    GMAIL_READ_ONLY_SCOPE,
    THREAD_POOL_MAX_WORKERS,
    MAX_RETRIES,
    RETRY_DELAY,
    RETRY_BACKOFF_FACTOR,
)
from gmail_fisher.data.models import GmailMessage, MessageAttachment

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
                try:
                    credentials.refresh(Request())
                except RefreshError:
                    logger.warning("Stored token is invalid or revoked — re-authenticating via browser")
                    credentials = None
            if not credentials or not credentials.valid:
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
    def _retry_api_call(cls, func, *args, **kwargs):
        """
        Retry wrapper for API calls with exponential backoff.
        Handles timeout errors and other transient failures.
        """
        last_exception = None
        for attempt in range(MAX_RETRIES + 1):
            try:
                return func(*args, **kwargs)
            except (socket.timeout, OSError, HttpError) as e:
                last_exception = e
                if attempt == MAX_RETRIES:
                    logger.error(f"Max retries ({MAX_RETRIES}) exceeded for API call. Last error: {e}")
                    raise e

                # Calculate delay with exponential backoff
                delay = RETRY_DELAY * (RETRY_BACKOFF_FACTOR ** attempt)
                logger.warning(f"API call failed (attempt {attempt + 1}/{MAX_RETRIES + 1}): {e}. Retrying in {delay:.2f}s...")
                time.sleep(delay)

        # This should never be reached, but just in case
        raise last_exception

    @classmethod
    def list_message_ids(
        cls, sender_emails: str, keywords: str, max_results: int
    ) -> Iterable[str]:
        """
        For a given sender email and comma-separated keywords, retrieve the matching
        message IDs and return them as a list.
        """
        logger.info(f"Fetching emails with {sender_emails=}, {keywords=}")

        def _make_api_call():
            return (
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

        list_message_results = cls._retry_api_call(_make_api_call)

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
        failed_messages = []
        message_ids = GmailGateway.list_message_ids(
            sender_emails, keywords, max_results
        )

        with ThreadPoolExecutor(max_workers=THREAD_POOL_MAX_WORKERS) as pool:
            num_messages = len(list(message_ids))
            logger.info(
                f"⏳  Fetching {num_messages} email messages from Gmail API with thread pool..."
            )
            with alive_bar(num_messages) as bar:
                futures = [
                    pool.submit(GmailGateway._get_message_detail_with_retry, message_id, fetch_body)
                    for message_id in message_ids
                ]

                for future in concurrent.futures.as_completed(futures):
                    try:
                        result = future.result()
                        if result is not None:
                            results.append(result)
                        else:
                            failed_messages.append("unknown_id")
                        bar()
                    except Exception as ex:
                        logger.error(f"Error fetching future result {ex}")
                        failed_messages.append("unknown_id")
                        bar()

        if failed_messages:
            logger.warning(f"Failed to fetch {len(failed_messages)} messages due to persistent errors")

        logger.success(
            f"Successfully fetched {len(results)} emails from Gmail API from {sender_emails=} and {keywords=}"
        )

        return results

    @classmethod
    def _get_message_detail_with_retry(cls, message_id: str, fetch_body: bool) -> Optional[GmailMessage]:
        """
        Wrapper for get_message_detail with retry logic.
        Returns None if all retries fail.
        """
        try:
            return cls._retry_api_call(cls._get_message_detail_internal, message_id, fetch_body)
        except Exception as e:
            logger.error(f"Failed to fetch message {message_id} after {MAX_RETRIES} retries: {e}")
            return None

    @classmethod
    def _get_message_detail_internal(cls, message_id: str, fetch_body: bool) -> GmailMessage:
        """
        Internal method for fetching message details (used by retry wrapper).
        """
        get_message_result = (
            GmailClient.get_instance()
            .users()
            .messages()
            .get(id=message_id, userId="me")
            .execute(http=GmailClient.auth_http_request())
        )

        attachment_list = GmailGateway.get_message_attachments(
            get_message_result["payload"]
        )
        message_date = next(
            item
            for item in get_message_result["payload"]["headers"]
            if item["name"] == "Date"
        )["value"]

        message_subject = get_message_result["snippet"]
        message = GmailMessage(
            id=message_id,
            subject=message_subject,
            date=message_date,
            attachments=attachment_list,
        )

        if not fetch_body:
            return message

        message.body = GmailGateway.get_message_body(get_message_result["payload"])

        return message

    @classmethod
    def get_message_detail(cls, message_id: str, fetch_body: bool) -> GmailMessage:
        """
        Fetches the detail of a message with a given message ID.
        """
        return cls._get_message_detail_with_retry(message_id, fetch_body)

    @classmethod
    def get_message_body(cls, message_payload: Dict[str, Any]) -> str:
        try:
            if message_payload["body"]["size"] == 0:
                message_parts = message_payload.get("parts", None)
                return (
                    base64.urlsafe_b64decode(message_parts[0]["body"]["data"])
                    .decode("utf-8")
                    .replace("\n", "")
                )
            else:
                return (
                    base64.urlsafe_b64decode(message_payload["body"]["data"])
                    .decode("utf-8")
                    .replace("\n", "")
                )
        except Exception as e:
            logger.error(f"ERROR parsing body {e}")

    @classmethod
    def get_message_attachments(cls, message_payload: Dict[str, Any]):
        attachment_list = list()
        attachment = None
        if message_payload.keys().__contains__("parts"):
            for part in message_payload["parts"]:
                match part["mimeType"]:
                    case "application/pdf" | "application/octet-stream":
                        attachment = MessageAttachment(
                            part_id=part["partId"],
                            filename=part["filename"],
                            id=part["body"]["attachmentId"],
                        )
                    case "multipart/mixed":
                        for subpart in part["parts"]:
                            if subpart["mimeType"].__contains__("pdf"):
                                attachment = MessageAttachment(
                                    part_id=subpart["partId"],
                                    filename=subpart["filename"],
                                    id=subpart["body"]["attachmentId"],
                                )
                if attachment:
                    attachment_list.append(attachment)

        return attachment_list

    @classmethod
    def get_message_attachment(cls, message_id: str, attachment_id: str) -> str:
        """
        Returns a base-64 string with the content for the .pdf attachment with 'message_id'
        and 'attachment_id'.
        """
        def _make_api_call():
            return (
                GmailClient.get_instance()
                .users()
                .messages()
                .attachments()
                .get(userId="me", messageId=message_id, id=attachment_id)
                .execute(http=GmailClient.auth_http_request())["data"]
            )

        return cls._retry_api_call(_make_api_call)
