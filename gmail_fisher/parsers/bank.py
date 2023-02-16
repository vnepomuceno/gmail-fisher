import json
import re
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable, Final

import pdfplumber

from gmail_fisher import get_logger
from gmail_fisher.utils.config import TEMP_PATH
from gmail_fisher.api.gateway import GmailGateway
from gmail_fisher.data.models import BankExpense
from gmail_fisher.utils.file_utils import FileUtils

logger = get_logger(__name__)


class BankStatementParser(ABC):
    @classmethod
    @abstractmethod
    def fetch_expenses(cls) -> Iterable[BankExpense]:
        pass

    @classmethod
    def serialize_expenses_to_json_file(
        cls, expenses: [BankExpense], output_path: Path
    ) -> str:
        logger.info(f"Exporting bank expenses to {output_path=}")
        if not output_path.parent.exists():
            output_path.parent.mkdir(exist_ok=True)
        file = open(output_path, "w")
        sorted_expenses = sorted(expenses, key=lambda exp: exp.date, reverse=True)
        json_expenses = json.dumps(
            [expense.__dict__ for expense in sorted_expenses],
            ensure_ascii=False,
            indent=4,
        )
        file.write(json_expenses)
        file.close()
        logger.success(f"Successfully written results to {output_path=}")
        return json_expenses


class BancoCttParser(BankStatementParser):
    sender_email: Final[str] = "documentos@bancoctt.pt"
    keywords: Final[str] = "Extrato"

    @classmethod
    def fetch_expenses(cls) -> Iterable[BankExpense]:
        logger.info("Fetching Banco CTT monthly statements")
        messages = GmailGateway.get_email_messages(
            sender_emails=cls.sender_email,
            keywords=cls.keywords,
            max_results=1000,
            fetch_body=True,
        )
        bank_expenses = []
        for message in messages:
            attachment_b64_str_content = GmailGateway.get_message_attachment(
                message_id=message.id, attachment_id=message.attachments[0].id
            )

            filename = messages[0].id
            temp_filepath = TEMP_PATH / filename
            FileUtils.save_base64_pdf(
                base64_string=attachment_b64_str_content,
                file_path=temp_filepath,
                message_id=filename,
            )
            expenses = cls.parse_expenses_from_messages(temp_filepath)
            bank_expenses.append(expenses)

        shutil.rmtree(TEMP_PATH)

        return [item for sublist in bank_expenses for item in sublist]

    @classmethod
    def parse_expenses_from_messages(cls, pdf_statement: Path) -> Iterable[BankExpense]:
        logger.info(f"Parsing Banco CTT statement for path={pdf_statement}")
        transaction_lines = cls.get_rendered_text_from_pdf(pdf_statement)
        expenses = [
            BankExpense(
                id=line.split(" ")[-3],
                description=" ".join(line.split(" ")[2:-3]),
                total_euros=line.split(" ")[-2],
                date=cls.get_yyyy_mm_dd_date(line.split(" ")[1]),
            )
            for line in transaction_lines
        ]

        return expenses

    @classmethod
    def get_rendered_text_from_pdf(cls, pdf_file: Path) -> Iterable[Iterable[str]]:
        pdf = pdfplumber.open(pdf_file)
        page_lines = [page.extract_text().split("\n") for page in pdf.pages]

        transaction_lines = []
        for page in page_lines:
            for line in page:
                pattern = re.compile(r"^\d\d-\d\d-\d\d\d\d \d\d-\d\d-\d\d\d\d")
                matches = pattern.findall(line)
                if len(matches) != 0:
                    transaction_lines.append(line)

        logger.success(f"Extracted transaction lines:")
        for line in transaction_lines:
            logger.success(line)
        return transaction_lines

    @classmethod
    def get_yyyy_mm_dd_date(cls, dd_mm_yyyy_date: str) -> str:
        str_arr = dd_mm_yyyy_date.split("-")
        return f"{str_arr[2]}-{str_arr[1]}-{str_arr[0]}"


if __name__ == "__main__":
    BancoCttParser.fetch_expenses()
