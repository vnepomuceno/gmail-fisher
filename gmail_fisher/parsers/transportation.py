import json
import re
from datetime import datetime
from typing import Iterable, Tuple, Final

import dateutil
import html2text
from alive_progress import alive_bar

from gmail_fisher.gateway import GmailGateway
from gmail_fisher.data.models import (
    TransportationExpense,
    BoltTransportationExpense,
    GmailMessage,
)
from gmail_fisher.parsers import print_header
from gmail_fisher.utils import get_logger

logger = get_logger(__name__)


class TransportationExpenseParser:
    @classmethod
    def fetch_expenses(cls) -> Iterable[TransportationExpense]:
        pass

    @classmethod
    def serialize_expenses_to_json_file(
        cls, expenses: [TransportationExpense], output_path: str
    ) -> str:
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


class BoltParser(TransportationExpenseParser):
    sender_email: Final[str] = "receipts-portugal@bolt.eu"
    keywords: Final[str] = "bolt trip"

    @classmethod
    def fetch_expenses(cls) -> Iterable[BoltTransportationExpense]:
        print_header("Bolt")
        logger.info("Fetching Bolt transportation expenses")
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
    ) -> Iterable[BoltTransportationExpense]:
        expenses = []
        num_messages = len(list(gmail_messages))
        logger.info(
            f"⏳  Mapping {num_messages} email messages to Bolt transportation expenses..."
        )
        with alive_bar(num_messages) as bar:
            for message in gmail_messages:
                try:
                    from_address, to_address = cls.__get_addresses(message)
                    expenses.append(
                        BoltTransportationExpense(
                            id=message.id,
                            distance_km=cls.__get_distance_km(message),
                            from_address=from_address,
                            to_address=to_address,
                            total=cls.__get_total_payed(message),
                            date=cls.__get_date(message),
                        )
                    )
                    bar()
                except IndexError:
                    logger.error(
                        f"Error fetching Bolt expense from email message with subject={message.subject}"
                    )

        return expenses

    @classmethod
    def __get_distance_km(cls, message) -> int:
        match = 0
        try:
            if re.search("distance .* km", message.subject) is not None:
                return int(
                    re.search("distance .* km", message.subject).group().split(" ")[1]
                )
            else:
                body = html2text.html2text(message.body)
                lines_with_distances = [
                    line for line in body.split("\n") if line.__contains__("km")
                ]
                return int(lines_with_distances[0].split("•")[1].split("km")[0])
        except Exception as e:
            logger.warning(
                f"Could not match distance (km) from subject='{message.subject}'"
            )

    @classmethod
    def __get_addresses(cls, message) -> Tuple[str, str]:
        from_address, to_address = "", ""
        try:
            if (
                re.search(
                    "[0-9][0-9]:[0-9][0-9] .* [0-9][0-9]:[0-9][0-9]", message.subject
                )
                is not None
            ):
                both_addresses = re.search(
                    "[0-9][0-9]:[0-9][0-9] .* [0-9][0-9]:[0-9][0-9]", message.subject
                ).group()
                from_address = both_addresses.split(":")[1][
                    3 : (len(both_addresses.split(":")[1]) - 3)
                ]
                to_address = both_addresses.split(":")[2][
                    3 : (len(both_addresses.split(":")[2]) - 3)
                ]
            else:
                pickup_and_dropoff = (
                    html2text.html2text(message.body)
                    .split("Pickup:  \n--")[1]
                    .split("\n|  \n---")[0]
                )
                locations_array = [
                    blob.strip().replace("\n", "")
                    for blob in pickup_and_dropoff.split("|  |")
                ]
                from_address = locations_array[0].strip("-  ").split("  ")[0]
                to_address = locations_array[1].strip("Dropoff:  -- ").split("  ")[0]
        except Exception as e:
            logger.warning(
                f"Could not match addresses with subject='{message.subject}', error={e}"
            )

        return from_address, to_address

    @classmethod
    def __get_total_payed(cls, message) -> float:
        match = 0
        try:
            if re.search("Total .*€", message.subject) is not None:
                return float(
                    re.search("Total .*€", message.subject)
                    .group()
                    .split("Total ")[1]
                    .split("€")[0]
                )
            else:
                body = html2text.html2text(message.body)
                lines_with_totals = [
                    line for line in body.split("\n") if line.__contains__("Total")
                ]
                return float(lines_with_totals[0].split(":")[1].strip().split("€")[0])
        except Exception as e:
            logger.warning(
                f"Could not match total payed (€) with subject='{message.subject}', error={e}"
            )

    @classmethod
    def __get_date(cls, message) -> str:
        try:
            if re.match(".*[1-3][0-9]{3}", message.subject) is not None:
                return str(
                    datetime(
                        int(message.subject[0:10].split(".")[2]),
                        int(message.subject[0:10].split(".")[1]),
                        int(message.subject[0:10].split(".")[0]),
                    )
                )[:10]
            else:
                lines_with_dates = [
                    line
                    for line in html2text.html2text(message.body).split("\n")
                    if re.match(".*[1-3][0-9]{3}", line)
                ]
                return str(dateutil.parser.parse(lines_with_dates[0]).date())
        except Exception as e:
            logger.warning(
                f"Could not match date with subject='{message.subject}', {e}"
            )
            return ""
