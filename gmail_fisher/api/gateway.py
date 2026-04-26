import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Final, Optional

import google_auth_httplib2
import httplib2
from alive_progress import alive_bar
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource

from gmail_fisher import get_logger
from gmail_fisher.utils.config import (
    AUTH_PATH,
    GMAIL_READ_ONLY_SCOPE,
    THREAD_POOL_MAX_WORKERS,
)
from gmail_fisher.data.models import GmailMessage, MessageAttachment

logger = get_logger(__name__)

_USER_ID = "me"


class GmailClient:
    scopes: list[str] = [GMAIL_READ_ONLY_SCOPE]
    credentials_path: Final[Path] = AUTH_PATH / "credentials.json"
    token_path: Final[Path] = AUTH_PATH / "auth_token.json"
    _instance: Resource = None

    @classmethod
    def auth_http_request(cls) -> google_auth_httplib2.AuthorizedHttp:
        return google_auth_httplib2.AuthorizedHttp(
            cls._authenticate(), http=httplib2.Http()
        )

    @classmethod
    def get_instance(cls) -> Resource:
        if not cls._instance:
            cls._instance = build("gmail", "v1", credentials=cls._authenticate())
        return cls._instance

    @classmethod
    def _authenticate(cls) -> Credentials:
        credentials = cls._load_cached_credentials()
        if not credentials or not credentials.valid:
            credentials = cls._refresh_or_reauthorize(credentials)
            cls._save_credentials(credentials)
        return credentials

    @classmethod
    def _load_cached_credentials(cls) -> Optional[Credentials]:
        if cls.token_path.exists():
            return Credentials.from_authorized_user_file(str(cls.token_path), cls.scopes)
        return None

    @classmethod
    def _refresh_or_reauthorize(cls, credentials: Optional[Credentials]) -> Credentials:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            return credentials
        flow = InstalledAppFlow.from_client_secrets_file(
            str(cls.credentials_path), cls.scopes
        )
        return flow.run_local_server(port=0)

    @classmethod
    def _save_credentials(cls, credentials: Credentials) -> None:
        with open(cls.token_path, "w") as token:
            token.write(credentials.to_json())


class GmailGateway:
    @classmethod
    def list_message_ids(
        cls, sender_emails: str, keywords: str, max_results: int
    ) -> list[str]:
        logger.info(f"Fetching emails with {sender_emails=}, {keywords=}")
        result = (
            GmailClient.get_instance()
            .users()
            .messages()
            .list(
                userId=_USER_ID,
                q=f"from:{sender_emails} {keywords}",
                maxResults=max_results,
            )
            .execute(http=GmailClient.auth_http_request())
        )

        if result["resultSizeEstimate"] == 0:
            logger.warning(
                f"No messages found for email='{sender_emails}', keywords='{keywords}'"
            )
            return []

        message_ids = [message["id"] for message in result["messages"]]
        logger.info(f"Found {len(message_ids)} emails for {sender_emails=}, {keywords=}")
        return message_ids

    @classmethod
    def get_email_messages(
        cls,
        sender_emails: str,
        keywords: str,
        max_results: int,
        fetch_body: bool = False,
    ) -> list[GmailMessage]:
        message_ids = cls.list_message_ids(sender_emails, keywords, max_results)
        num_messages = len(message_ids)
        logger.info(
            f"⏳  Fetching {num_messages} email messages from Gmail API with thread pool..."
        )

        results = []
        with ThreadPoolExecutor(max_workers=THREAD_POOL_MAX_WORKERS) as pool:
            futures = [
                pool.submit(cls.get_message_detail, message_id, fetch_body)
                for message_id in message_ids
            ]
            with alive_bar(num_messages) as bar:
                for future in as_completed(futures):
                    try:
                        results.append(future.result())
                        bar()
                    except Exception as ex:
                        logger.error(f"Error fetching future result: {ex}")

        logger.success(
            f"Successfully fetched {len(results)} emails from Gmail API from {sender_emails=} and {keywords=}"
        )
        return results

    @classmethod
    def get_message_detail(cls, message_id: str, fetch_body: bool) -> GmailMessage:
        raw = (
            GmailClient.get_instance()
            .users()
            .messages()
            .get(id=message_id, userId=_USER_ID)
            .execute(http=GmailClient.auth_http_request())
        )
        payload = raw["payload"]

        message = GmailMessage(
            id=message_id,
            subject=raw["snippet"],
            date=cls._extract_date_header(payload),
            attachments=cls.get_message_attachments(payload),
        )

        if fetch_body:
            message.body = cls.get_message_body(payload)

        return message

    @classmethod
    def _extract_date_header(cls, payload: dict[str, Any]) -> str:
        return next(
            header["value"]
            for header in payload["headers"]
            if header["name"] == "Date"
        )

    @classmethod
    def get_message_body(cls, payload: dict[str, Any]) -> Optional[str]:
        try:
            data = (
                payload["parts"][0]["body"]["data"]
                if payload["body"]["size"] == 0
                else payload["body"]["data"]
            )
            return base64.urlsafe_b64decode(data).decode("utf-8").replace("\n", "")
        except Exception as e:
            logger.error(f"Error parsing message body: {e}")
            return None

    @classmethod
    def get_message_attachments(cls, payload: dict[str, Any]) -> list[MessageAttachment]:
        if "parts" not in payload:
            return []

        attachments = []
        for part in payload["parts"]:
            attachment = cls._extract_attachment_from_part(part)
            if attachment:
                attachments.append(attachment)
        return attachments

    @classmethod
    def _extract_attachment_from_part(
        cls, part: dict[str, Any]
    ) -> Optional[MessageAttachment]:
        mime_type = part["mimeType"]
        if mime_type in ("application/pdf", "application/octet-stream"):
            return MessageAttachment(
                part_id=part["partId"],
                filename=part["filename"],
                id=part["body"]["attachmentId"],
            )
        if mime_type == "multipart/mixed":
            for subpart in part["parts"]:
                if "pdf" in subpart["mimeType"]:
                    return MessageAttachment(
                        part_id=subpart["partId"],
                        filename=subpart["filename"],
                        id=subpart["body"]["attachmentId"],
                    )
        return None

    @classmethod
    def get_message_attachment(cls, message_id: str, attachment_id: str) -> str:
        return (
            GmailClient.get_instance()
            .users()
            .messages()
            .attachments()
            .get(userId=_USER_ID, messageId=message_id, id=attachment_id)
            .execute(http=GmailClient.auth_http_request())["data"]
        )
