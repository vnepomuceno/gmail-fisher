import json
import logging
import re
from typing import Iterable, Optional

from .gmail_gateway import GmailGateway
from .models import (
    GmailMessage,
    UberEatsExpense,
    BoltFoodExpense,
    FoodExpense,
    expense_date_attribute,
)


class FoodExpenseParser:
    @classmethod
    def fetch_expenses(cls) -> Iterable[FoodExpense]:
        pass

    @classmethod
    def serialize_expenses_to_json_file(
        cls, expenses: [FoodExpense], json_filepath: str
    ) -> str:
        file = open(json_filepath, "w")
        sorted_expenses = sorted(expenses, key=expense_date_attribute, reverse=True)
        json_expenses = json.dumps(
            [expense.__dict__ for expense in sorted_expenses], ensure_ascii=False
        )
        file.write(json_expenses)
        file.close()
        return json_expenses


class BoltFoodParser(FoodExpenseParser):
    __SENDER_EMAIL = "portugal-food@bolt.eu"
    __KEYWORDS = "Delivery from Bolt Food"

    @classmethod
    def fetch_expenses(cls) -> Iterable[FoodExpense]:
        logging.info("Fetching Bolt Food expenses")
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
    ) -> [BoltFoodExpense]:
        expenses = []
        for message in gmail_messages:
            try:
                restaurant_str = re.search(r"From .* -", message.subject).group()[5:-2]
                restaurant = (
                    restaurant_str.replace(
                        " - Saldanha Avenida Casal Ribeiro, 50 B , 1000-093 To Praça Aniceto do Rosário, Lisbon 1 Hamburguer X",
                        "",
                    )
                    .replace(" - Saldanha Av. Miguel Bombarda, 23B", "")
                    .replace(
                        " Rua do saco 50, 1150-284 Lisboa To Praça Aniceto do Rosário, Lisbon 1 🎁 2x1",
                        "",
                    )
                    .replace("&#39;", "'")
                )
                date_arr = message.subject.split(" ")[0].split("-")
                date = f"{date_arr[2]}-{date_arr[1]}-{date_arr[0]}"
                total = cls.__get_bolt_total_payed_from_body(message)
                expenses.append(
                    BoltFoodExpense(restaurant=restaurant, total=total, date=date)
                )
                logging.info(f"RESTAURANT: {restaurant}")
            except Exception as ex:
                logging.error(f"ERROR for subject={message.subject}")

        return expenses

    @staticmethod
    def __get_bolt_total_payed_from_body(message: GmailMessage) -> Optional[float]:
        try:
            return float(
                re.search(r"\*[0-9]*[0-9]+.[0-9][0-9]€\*", message.body)
                .group(0)
                .replace("€", "")
                .replace("*", "")
            )
        except Exception as ex:
            logging.error(f"Raised exception when get Bolt total {ex}")
            return None


class UberEatsParser(FoodExpenseParser):
    __SENDER_EMAIL = "uber.portugal@uber.com"
    __KEYWORDS = "Total"

    @classmethod
    def fetch_expenses(cls) -> Iterable[FoodExpense]:
        logging.info("Fetching UberEats food expenses")
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
    ) -> [UberEatsExpense]:
        expenses = []
        for message in gmail_messages:
            try:
                expenses.append(
                    UberEatsExpense(
                        restaurant=message.subject.split("receipt for ")[1]
                        .split(".")[0]
                        .replace("&#39;", "'")
                        .replace("&amp;", "&")
                        .replace("\u00ae", "")
                        .replace(" 🐠", "")
                        .replace(" (Marquês de Pombal)", "")
                        .replace("® (Saldanha)", "")
                        .replace(" (Saldanha)", "")
                        .replace(" (General Roçadas)", "")
                        .replace(" (Fontes Pereira de Melo)", "")
                        .replace(" (São Sebastião)", "")
                        .replace(" (Graça)", "")
                        .replace(" (Monumental)", "")
                        .replace(" (Saldanha Residence)", "")
                        .replace(" (República)", "")
                        .replace(" (Sta", "")
                        .replace(" (Barata Salgueiro)", "")
                        .replace(" (Rossio)", ""),
                        total=float(message.subject.split(" ")[1].replace("€", "")),
                        date=message.get_date_as_datetime().date().__str__(),
                    )
                )
            except IndexError:
                logging.error(
                    f"Error fetching UberEats expense from email message with subject={message.subject}"
                )

        return expenses
