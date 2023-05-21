import json
import os
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable, Optional, Final

import html2text as html2text
from alive_progress import alive_bar

from gmail_fisher import get_logger, ROOT_DIR
from gmail_fisher.api.gateway import GmailGateway
from gmail_fisher.data.models import (
    GmailMessage,
    UberEatsExpense,
    BoltFoodExpense,
    FoodExpense,
)
from gmail_fisher.parsers import print_header
from gmail_fisher.utils.json_utils import JsonUtils

logger = get_logger(__name__)


def apply_restaurant_filter(func):
    def wrapper(*args, **kwargs):
        return FoodExpenseParser.apply_restaurant_filters(func(*args, **kwargs))

    return wrapper


class FoodExpenseParser(ABC):
    @classmethod
    @abstractmethod
    def fetch_expenses(cls) -> Iterable[FoodExpense]:
        pass

    @classmethod
    def serialize_expenses_to_json_file(
        cls, expenses: [FoodExpense], output_path: str
    ) -> str:
        logger.info(f"Exporting food expenses to {output_path=}")
        output_path = Path(output_path)
        if not output_path.parent.exists():
            output_path.parent.mkdir(exist_ok=True)

        sorted_expenses = sorted(expenses, key=lambda exp: exp.date, reverse=True)
        json_expenses = json.dumps(
            [expense.__dict__ for expense in sorted_expenses],
            ensure_ascii=False,
            indent=4,
        )

        JsonUtils.write_to_json_file(json_expenses, output_path)
        return json_expenses

    @classmethod
    def apply_restaurant_filters(cls, string_value: str) -> str:
        """
        Apply filters by finding the filters dict key and replacing it by the dict value
        """
        filters = JsonUtils.load_dict_from_json(
            os.path.join(ROOT_DIR, "parsers/restaurant-filters.json")
        )

        for filter_key, filter_value in filters["replace"].items():
            string_value = string_value.replace(filter_key, filter_value)
        for trim_str in filters["trim"]:
            string_value = string_value.replace(trim_str, "")

        return string_value


class BoltFoodParser(FoodExpenseParser):
    sender_email: Final[str] = "portugal-food@bolt.eu"
    keywords: Final[str] = "Delivery from Bolt Food"

    @classmethod
    def fetch_expenses(cls) -> Iterable[FoodExpense]:
        print_header("🍕   Bolt Food")
        messages = GmailGateway.get_email_messages(
            sender_emails=cls.sender_email,
            keywords=cls.keywords,
            max_results=1000,
            fetch_body=True,
        )
        return cls.parse_expenses_from_messages(messages)

    @classmethod
    def parse_expenses_from_messages(
        cls, gmail_messages: Iterable[GmailMessage]
    ) -> Iterable[BoltFoodExpense]:
        expenses = []
        num_messages = len(list(gmail_messages))
        logger.info(
            f"⏳  Mapping {num_messages} email messages to Bolt Food expenses..."
        )
        with alive_bar(num_messages) as bar:
            for message in gmail_messages:
                try:
                    expense = BoltFoodExpense(
                        id=message.id,
                        restaurant=cls.get_restaurant(message),
                        total=cls.get_total_payed(message=message),
                        date=cls.get_date(message),
                    )
                    expenses.append(expense)
                    bar()
                except Exception as ex:
                    logger.warning(
                        f"Could not map food expense with subject={message.subject}, error={ex}"
                    )

        logger.success(f"Successfully mapped {len(expenses)} Bolt Food expenses")
        return expenses

    @classmethod
    @apply_restaurant_filter
    def get_restaurant(cls, message: GmailMessage) -> Optional[str]:
        if re.search(r"From .* -", message.subject) is not None:
            restaurant = re.search(r"From .* -", message.subject).group()[5:-2]
        else:
            if re.search(r"From .*,", message.subject) is not None:
                restaurant = (
                    re.search(r"From .*,", message.subject).group().split(",")[0][5:]
                )
            else:
                raise Exception(
                    f"Cannot match restaurant for subject={message.subject}"
                )

        if restaurant.__contains__("-"):
            restaurant = restaurant.split("-")[0].strip()

        return restaurant

    @staticmethod
    def get_date(message: GmailMessage) -> str:
        date_arr = message.subject.split(" ")[0].split("-")
        return f"{date_arr[2]}-{date_arr[1]}-{date_arr[0]}"

    @staticmethod
    def get_total_payed(message: GmailMessage) -> Optional[float]:
        if message.body.__contains__("<html>"):
            body = html2text.html2text(message.body)
            body = body.split("**Total charged:**")[1]
        else:
            body = message.body

        try:
            return float(
                re.search(r"\*[0-9]*[0-9]+.[0-9][0-9]€\*", body)
                .group(0)
                .replace("€", "")
                .replace("*", "")
            )
        except Exception as ex:
            logger.error(f"ERROR when fetching total payed {ex}")
            return None


class UberEatsParser(FoodExpenseParser):
    sender_email: Final[str] = "uber.portugal@uber.com"
    keywords: Final[str] = "Total"

    @classmethod
    def fetch_expenses(cls) -> Iterable[FoodExpense]:
        logger.info("Fetching UberEats food expenses")
        print_header("🍕   Uber Eats")
        messages = GmailGateway.get_email_messages(
            sender_emails=cls.sender_email,
            keywords=cls.keywords,
            max_results=1000,
            fetch_body=False,
        )
        return cls.parse_expenses_from_messages(messages)

    @classmethod
    def parse_expenses_from_messages(
        cls, gmail_messages: Iterable[GmailMessage]
    ) -> Iterable[UberEatsExpense]:
        expenses = []
        num_messages = len(list(gmail_messages))
        with alive_bar(num_messages) as bar:
            for message in gmail_messages:
                try:
                    expense = UberEatsExpense(
                        id=message.id,
                        restaurant=cls.get_restaurant(message),
                        total=cls.get_total_payed(message),
                        date=cls.get_date(message),
                    )

                    expenses.append(expense)
                    bar()
                except IndexError:
                    logger.warning(
                        f"Could not map food expense with subject='{message.subject}'"
                    )

        return expenses

    @staticmethod
    @apply_restaurant_filter
    def get_restaurant(message: GmailMessage) -> Optional[str]:
        restaurant = message.subject.split("receipt for ")[1].split(".")[0]
        return restaurant

    @staticmethod
    def get_total_payed(message: GmailMessage) -> float:
        return float(message.subject.split(" ")[1].replace("€", ""))

    @staticmethod
    def get_date(message: GmailMessage):
        return message.get_date_as_datetime().date().__str__()
