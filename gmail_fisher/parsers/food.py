import json
import re
from pathlib import Path
from typing import Iterable, Optional

from gmail_fisher.gmail_gateway import GmailGateway
from gmail_fisher.models import (
    GmailMessage,
    UberEatsExpense,
    BoltFoodExpense,
    FoodExpense,
    expense_date_attribute,
)
from gmail_fisher.utils import get_logger

logger = get_logger(__name__)


class FoodExpenseParser:
    @classmethod
    def fetch_expenses(cls) -> Iterable[FoodExpense]:
        pass

    @classmethod
    def serialize_expenses_to_json_file(
        cls, expenses: [FoodExpense], json_filepath: str
    ) -> str:
        json_filepath = Path(json_filepath)
        if not json_filepath.parent.exists():
            json_filepath.parent.mkdir(exist_ok=True)
        file = open(json_filepath, "w")
        sorted_expenses = sorted(expenses, key=expense_date_attribute, reverse=True)
        json_expenses = json.dumps(
            [expense.__dict__ for expense in sorted_expenses],
            ensure_ascii=False,
            indent=4,
        )
        file.write(json_expenses)
        file.close()
        return json_expenses


class BoltFoodParser(FoodExpenseParser):
    __SENDER_EMAIL = "portugal-food@bolt.eu"
    __KEYWORDS = "Delivery from Bolt Food"
    __RESTAURANT_FILTERS = {
        " - Saldanha Avenida Casal Ribeiro, 50 B , 1000-093 To Praça Aniceto do Rosário, Lisbon 1 Hamburguer X": "",
        " - Saldanha Av. Miguel Bombarda, 23B": "",
        " Rua do saco 50, 1150-284 Lisboa To Praça Aniceto do Rosário, Lisbon 1 🎁 2x1": "",
        " - Av. Roma Avenida de Roma 74 B": "",
        "&#39;": "'",
        " Rua Marquês de Fronteira 117F": "",
        ", 1070-292 Lisboa To Praça Aniceto do Rosário, Lisbon 1 × 🎁 2x1": "",
    }

    @classmethod
    def fetch_expenses(cls) -> Iterable[FoodExpense]:
        logger.info("Fetching Bolt Food expenses")
        messages = GmailGateway.run_batch_get_message_detail(
            sender_emails=cls.__SENDER_EMAIL,
            keywords=cls.__KEYWORDS,
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
                restaurant = cls.__get_restaurant(message, cls.__RESTAURANT_FILTERS)
                total = cls.__get_total_payed(message)
                date = cls.__get_date(message)

                expenses.append(BoltFoodExpense(message.id, restaurant, total, date))
                logger.info(f"RESTAURANT: {restaurant}")
            except Exception as ex:
                logger.error(f"ERROR for subject={message.subject}")

        return expenses

    @staticmethod
    def __get_restaurant(
        message: GmailMessage, filters: dict[str, str]
    ) -> Optional[str]:
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

        for exclude_str, replace_str in filters.items():
            restaurant = restaurant.replace(exclude_str, replace_str)

        return restaurant

    @staticmethod
    def __get_date(message: GmailMessage) -> str:
        date_arr = message.subject.split(" ")[0].split("-")
        return f"{date_arr[2]}-{date_arr[1]}-{date_arr[0]}"

    @staticmethod
    def __get_total_payed(message: GmailMessage) -> Optional[float]:
        try:
            return float(
                re.search(r"\*[0-9]*[0-9]+.[0-9][0-9]€\*", message.body)
                .group(0)
                .replace("€", "")
                .replace("*", "")
            )
        except Exception as ex:
            logger.error(f"ERROR when fetching total payed {ex}")
            return None


class UberEatsParser(FoodExpenseParser):
    __SENDER_EMAIL = "uber.portugal@uber.com"
    __KEYWORDS = "Total"
    __RESTAURANT_FILTERS = {
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
        messages = GmailGateway.run_batch_get_message_detail(
            sender_emails=cls.__SENDER_EMAIL,
            keywords=cls.__KEYWORDS,
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
                restaurant = cls.__get_restaurant(message, cls.__RESTAURANT_FILTERS)
                total = cls.__get_total_payed(message)
                date = cls.__get_date(message)

                expenses.append(UberEatsExpense(message.id, restaurant, total, date))
            except IndexError:
                logger.error(
                    f"Error fetching UberEats expense from email message with subject={message.subject}"
                )

        return expenses

    @staticmethod
    def __get_restaurant(
        message: GmailMessage, filters: dict[str, str]
    ) -> Optional[str]:
        restaurant = message.subject.split("receipt for ")[1].split(".")[0]
        for exclude_str, replace_str in filters.items():
            restaurant = restaurant.replace(exclude_str, replace_str)

        return restaurant

    @staticmethod
    def __get_total_payed(message: GmailMessage) -> float:
        return float(message.subject.split(" ")[1].replace("€", ""))

    @staticmethod
    def __get_date(message: GmailMessage):
        return message.get_date_as_datetime().date().__str__()
