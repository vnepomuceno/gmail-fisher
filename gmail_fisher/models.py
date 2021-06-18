import logging
import re
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class MessageAttachment:
    part_id: str
    filename: str
    id: str


@dataclass
class GmailMessage:
    id: str
    subject: str
    date: datetime
    attachments: List[MessageAttachment]
    body: Optional[str] = None

    def get_total_payed_from_subject(self) -> float:
        """
        Fetches message subject in format e.g. '... €15.40 ...' and returns
        a float equivalent to the total payed, or 0 if there is not match.
        """
        try:
            match = re.search("[€][1-9]?[0-9].[0-9][0-9]", self.subject).group(0)
        except AttributeError:
            logging.warning(
                f"Could not match total payed (e.g. €12.30) with message_id='{self.id}'"
            )

            return 0
        return float(match.strip("€"))

    def get_date_as_datetime(self) -> datetime:
        """
        Fetches message date in the format e.g. 'Sun, 29 Nov 2020 21:32:07 +0000 (UTC)',
        and returns a datetime with precision up to the day.
        """
        date_arr = self.date.strip(" +0000 (UTC)").split(", ")[1].split(" ")
        date_str = f"{date_arr[0]} {date_arr[1]} {date_arr[2]}"

        try:
            return datetime.strptime(date_str, "%d %b %Y")
        except ValueError as ve:
            logging.warning(
                f"Date could not be parsed with date='{date_str}', error='{ve}'"
            )
            return datetime.datetime.now()

    def ignore_message(self) -> bool:
        """
        Fetches message subject and returns True if it contains the word 'Refund' or
        if there is no total payed matched in that subject, or False otherwise.
        """
        if "Refund" in self.subject or self.get_total_payed_from_subject() == 0:
            return True
        else:
            return False


class FoodOrderService:
    UBER_EATS = "Uber Eats"
    BOLT_FOOD = "Bolt Food"


@dataclass
class FoodExpense:
    service: FoodOrderService
    restaurant: str
    total: float
    date: str


def expense_date_attribute(expense: FoodExpense):
    return expense.date


@dataclass
class UberEatsExpense(FoodExpense):
    def __init__(self, restaurant: str, total: float, date: datetime):
        self.service = FoodOrderService.UBER_EATS
        self.restaurant = restaurant
        self.total = total
        self.date = date


@dataclass
class BoltFoodExpense(FoodExpense):
    def __init__(self, restaurant: str, total: float, date: str):
        self.service = FoodOrderService.BOLT_FOOD
        self.restaurant = restaurant
        self.total = total
        self.date = date


class TransportationService:
    BOLT = "Bolt"


@dataclass
class TransportationExpense:
    service: TransportationService
    distance_km: int
    from_address: str
    to_address: str
    total: float
    date: str


@dataclass
class BoltTransportationExpense(TransportationExpense):
    def __init__(
        self,
        distance_km: int,
        from_address: str,
        to_address: str,
        total: float,
        date: str,
    ):
        self.service = TransportationService.BOLT
        self.distance_km = distance_km
        self.from_address = from_address
        self.to_address = to_address
        self.total = total
        self.date = date


def expense_date_attribute_transport(expense: TransportationExpense):
    return expense.date
