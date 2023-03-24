import json
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable, Optional, Final, Dict

import html2text as html2text
from alive_progress import alive_bar

from gmail_fisher import get_logger
from gmail_fisher.api.gateway import GmailGateway
from gmail_fisher.data.models import (
    GmailMessage,
    UberEatsExpense,
    BoltFoodExpense,
    FoodExpense,
)
from gmail_fisher.parsers import print_header

logger = get_logger(__name__)


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

    @classmethod
    def find_and_replace_string_value(
        cls, string_value: str, filters: dict[str, str]
    ) -> str:
        """
        Apply filters by finding the filters dict key and replacing it by the dict value
        """
        for exclude_str, replace_str in filters.items():
            string_value = string_value.replace(exclude_str, replace_str)
        return string_value


class BoltFoodParser(FoodExpenseParser):
    sender_email: Final[str] = "portugal-food@bolt.eu"
    keywords: Final[str] = "Delivery from Bolt Food"
    restaurant_filters: Final[Dict[str, str]] = {
        " - Saldanha Avenida Casal Ribeiro, 50 B , 1000-093 To Praça Aniceto do Rosário, Lisbon 1 Hamburguer X": "",
        " - Saldanha Av. Miguel Bombarda, 23B": "",
        " Rua do saco 50, 1150-284 Lisboa To Praça Aniceto do Rosário, Lisbon 1 🎁 2x1": "",
        " - Av. Roma Avenida de Roma 74 B": "",
        "&#39;": "'",
        " Rua Marquês de Fronteira 117F": "",
        ", 1070-292 Lisboa To Praça Aniceto do Rosário, Lisbon 1 × 🎁 2x1": "",
        " Av. Da República, 97 B": "",
        ", 1070": "",
        " Praça do Chile 8 Lisboa 1000": "",
    }

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

        return FoodExpenseParser.find_and_replace_string_value(
            restaurant, cls.restaurant_filters
        )

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
    restaurant_filters: Final[Dict[str, str]] = {
        "&#39;": "'",
        "&amp;": "&",
        "\u00ae": "",
        " 🐠": "",
        " (Marquês de Pombal)": "",
        "® (Saldanha)": "",
        " (Saldanha)": "",
        " (General Roçadas)": "",
        " (Fontes Pereira de Melo)": "",
        " (São Sebastião)": "",
        " (Graça)": "",
        " (Monumental)": "",
        " (Saldanha Residence)": "",
        " (República)": "",
        " (Sta": "",
        " (Barata Salgueiro)": "",
        " (Rossio)": "",
    }

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
                        restaurant=cls.get_restaurant(message, cls.restaurant_filters),
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
    def get_restaurant(message: GmailMessage, filters: dict[str, str]) -> Optional[str]:
        restaurant = message.subject.split("receipt for ")[1].split(".")[0]
        return FoodExpenseParser.find_and_replace_string_value(restaurant, filters)

    @staticmethod
    def get_total_payed(message: GmailMessage) -> float:
        return float(message.subject.split(" ")[1].replace("€", ""))

    @staticmethod
    def get_date(message: GmailMessage):
        return message.get_date_as_datetime().date().__str__()
