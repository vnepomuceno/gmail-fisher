import json
import logging
import re
from datetime import datetime
from typing import Iterable, Tuple

from gmail_fisher.gmail_gateway import GmailGateway
from gmail_fisher.models import (
    TransportationExpense,
    expense_date_attribute_transport,
    BoltTransportationExpense,
    GmailMessage,
)


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
                        id=message.id,
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
            date = str(
                datetime(
                    int(message.subject[1:10].split(".")[2]),
                    int(message.subject[1:10].split(".")[1]),
                    int(message.subject[1:10].split(".")[0]),
                )
            )[:10]
        except Exception as e:
            logging.warning(f"Could not match date with message_id='{message.id}', {e}")
            date = ""
        return date
