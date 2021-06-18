import json
import logging
import re
from datetime import datetime
from typing import Iterable, Optional, Tuple

from .gmail_gateway import GmailGateway
from .models import (
    GmailMessage,
    UberEatsExpense,
    BoltFoodExpense,
    FoodExpense,
    expense_date_attribute,
    TransportationExpense,
    expense_date_attribute_transport,
    BoltTransportationExpense,
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
    __RESTAURANT_FILTERS = {
        " - Saldanha Avenida Casal Ribeiro, 50 B , 1000-093 To Praça Aniceto do Rosário, Lisbon 1 Hamburguer X": "",
        " - Saldanha Av. Miguel Bombarda, 23B": "",
        " Rua do saco 50, 1150-284 Lisboa To Praça Aniceto do Rosário, Lisbon 1 🎁 2x1": "",
        " - Av. Roma Avenida de Roma 74 B": "",
        "&#39;": "'",
    }

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
    ) -> Iterable[BoltFoodExpense]:
        expenses = []
        for message in gmail_messages:
            try:
                restaurant = cls.__get_restaurant(message, cls.__RESTAURANT_FILTERS)
                total = cls.__get_total_payed(message)
                date = cls.__get_date(message)

                expenses.append(BoltFoodExpense(restaurant, total, date))
                logging.info(f"RESTAURANT: {restaurant}")
            except Exception as ex:
                logging.error(f"ERROR for subject={message.subject}")

        return expenses

    @staticmethod
    def __get_restaurant(
        message: GmailMessage, filters: dict[str, str]
    ) -> Optional[str]:
        restaurant = re.search(r"From .* -", message.subject).group()[5:-2]
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
            logging.error(f"Raised exception when get Bolt total {ex}")
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
    ) -> Iterable[UberEatsExpense]:
        expenses = []
        for message in gmail_messages:
            try:
                restaurant = cls.__get_restaurant(message, cls.__RESTAURANT_FILTERS)
                total = cls.__get_total_payed(message)
                date = cls.__get_date(message)

                expenses.append(UberEatsExpense(restaurant, total, date))
            except IndexError:
                logging.error(
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


class TransportationExpenseParser:
    @classmethod
    def fetch_expenses(cls) -> Iterable[TransportationExpense]:
        pass

    @classmethod
    def serialize_expenses_to_json_file(
        cls, expenses: [TransportationExpense], json_filepath: str
    ) -> str:
        file = open(json_filepath, "w")
        sorted_expenses = sorted(
            expenses, key=expense_date_attribute_transport, reverse=True
        )
        json_expenses = json.dumps(
            [expense.__dict__ for expense in sorted_expenses], ensure_ascii=False
        )
        file.write(json_expenses)
        file.close()
        return json_expenses


class BoltParser(TransportationExpenseParser):
    __SENDER_EMAIL = "receipts-portugal@bolt.eu"
    __KEYWORDS = "Your Bolt Trip On"

    @classmethod
    def fetch_expenses(cls) -> Iterable[BoltTransportationExpense]:
        logging.info("Fetching Bolt transportation expenses")
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
    ) -> Iterable[BoltTransportationExpense]:
        expenses = []
        for message in gmail_messages:
            try:
                distance_km: int = cls.__get_distance_km(message)
                from_address, to_address = cls.__get_addresses(message)
                total = cls.__get_total_payed(message)
                date = cls.__get_date(message)

                expenses.append(
                    BoltTransportationExpense(
                        distance_km=distance_km,
                        from_address=from_address,
                        to_address=to_address,
                        total=total,
                        date=date,
                    )
                )
            except IndexError:
                logging.error(
                    f"Error fetching Bolt expense from email message with subject={message.subject}"
                )

        return expenses

    @classmethod
    def __get_distance_km(cls, message) -> int:
        try:
            match = int(
                re.search("distance .* km", message.subject).group().split(" ")[1]
            )
        except AttributeError:
            logging.warning(
                f"Could not match distance (km) with message_id='{message.id}'"
            )
        return match

    @classmethod
    def __get_addresses(cls, message) -> Tuple[str, str]:
        try:
            both_addresses = re.search(
                "[0-9][0-9]:[0-9][0-9] .* [0-9][0-9]:[0-9][0-9]", message.subject
            ).group()
            from_address = both_addresses.split(":")[1][
                3 : (len(both_addresses.split(":")[1]) - 3)
            ]
            to_address = both_addresses.split(":")[2][
                3 : (len(both_addresses.split(":")[2]) - 3)
            ]
        except AttributeError:
            logging.warning(f"Could not match addresses with message_id='{message.id}'")
            from_address = to_address = ""
        return from_address, to_address

    @classmethod
    def __get_total_payed(cls, message) -> float:
        try:
            match = float(
                re.search("Total .*€", message.subject)
                .group()
                .split("Total ")[1]
                .split("€")[0]
            )
        except AttributeError:
            logging.warning(
                f"Could not match total payed (e.g. €12.30) with message_id='{message.id}'"
            )
        return match

    @classmethod
    def __get_date(cls, message) -> str:
        try:
            date = str(datetime(
                int(message.subject[1:10].split(".")[2]),
                int(message.subject[1:10].split(".")[1]),
                int(message.subject[1:10].split(".")[0]),
            ))[:10]
        except Exception as e:
            logging.warning(
                f"Could not match date with message_id='{message.id}', {e}"
            )
            date = ""
        return date
