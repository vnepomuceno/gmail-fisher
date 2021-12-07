import re
from abc import ABC, abstractmethod
from typing import Iterable, Optional, Final, Dict

import html2text as html2text

from gmail_fisher.gateway import GmailGateway
from gmail_fisher.models import (
    GmailMessage,
    UberEatsExpense,
    BoltFoodExpense,
    FoodExpense,
)
from gmail_fisher.io import get_logger

logger = get_logger(__name__)


class FoodExpenseParser(ABC):
    @classmethod
    @abstractmethod
    def fetch_expenses(cls) -> Iterable[FoodExpense]:
        pass

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
    }

    @classmethod
    def fetch_expenses(cls) -> Iterable[FoodExpense]:
        logger.info("Fetching Bolt Food expenses")
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
        for message in gmail_messages:
            try:
                expense = BoltFoodExpense(
                    id=message.id,
                    restaurant=cls.get_restaurant(message),
                    total=cls.get_total_payed(message=message),
                    date=cls.get_date(message),
                )
                expenses.append(expense)
                logger.info(f"Parsed bolt food expense {expense=}")
            except Exception as ex:
                logger.error(f"ERROR for subject={message.subject}")

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
        for message in gmail_messages:
            try:
                expense = UberEatsExpense(
                    id=message.id,
                    restaurant=cls.get_restaurant(message, cls.restaurant_filters),
                    total=cls.get_total_payed(message),
                    date=cls.get_date(message),
                )

                expenses.append(expense)
                logger.info(f"Parsed uber eats food expense {expense=}")
            except IndexError:
                logger.error(
                    f"Error fetching UberEats expense from email message with subject={message.subject}"
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
