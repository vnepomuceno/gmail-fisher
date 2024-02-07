from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Any

from pydantic import BaseModel

from gmail_fisher import get_logger

logger = get_logger(__name__)


class MessageAttachment(BaseModel):
    part_id: str
    filename: str
    id: str


class GmailMessage(BaseModel):
    id: str
    subject: str
    date: datetime
    attachments: Optional[List[MessageAttachment]] = None
    body: Optional[str] = None

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
            logger.warning(
                f"Date could not be parsed with date='{date_str}', error='{ve}'"
            )
            return datetime.datetime.now()


class FoodServiceType(BaseModel):
    UBER_EATS: str = "Uber Eats"
    BOLT_FOOD: str = "Bolt Food"
    ALL: str = "All"


class FoodExpense(BaseModel):
    id: str
    service: FoodServiceType
    restaurant: str
    total_euros: float
    date: str


class BankExpense(BaseModel):
    id: str
    description: str
    total_euros: str
    date: str

    def __init__(
        self, id: str, description: str, total_euros: str, date: str, /, **data: Any
    ):
        super().__init__(**data)
        self.id = id
        self.description = description
        self.total_euros = total_euros.replace("-", "")
        self.date = date
        self.transaction_type = self.get_transaction_type(total_euros)
        self.category = self.get_category(description)

    @staticmethod
    def get_transaction_type(total_euros: str):
        return "debit" if total_euros.__contains__("-") else "credit"

    @staticmethod
    def get_category(description: str):
        if description.__contains__("ACTIVPAYROLL"):
            return "salary"
        elif description.__contains__("CUF"):
            return "health"
        elif description.__contains__("AUCHAN"):
            return "supermarket"
        else:
            return "unknown"


@dataclass
class UberEatsExpense(FoodExpense):
    def __init__(
        self, id: str, restaurant: str, total: float, date: datetime, /, **data: Any
    ):
        super().__init__(**data)
        self.id = id
        self.service = FoodServiceType.UBER_EATS
        self.restaurant = restaurant
        self.total_euros = total
        self.date = date


@dataclass
class BoltFoodExpense(FoodExpense):
    def __init__(
        self, id: str, restaurant: str, total: float, date: str, /, **data: Any
    ):
        super().__init__(**data)
        self.id = id
        self.service = FoodServiceType.BOLT_FOOD
        self.restaurant = restaurant
        self.total_euros = total
        self.date = date


class TransportServiceType(BaseModel):
    BOLT: str = "Bolt"
    UBER: str = "Uber"


class TransportationExpense(BaseModel):
    id: str
    service: TransportServiceType
    distance_km: float
    from_address: str
    to_address: str
    total_euros: float
    # TODO Find a way to also scrap the time the transportation happened
    date: str


@dataclass
class BoltTransportationExpense(TransportationExpense):
    def __init__(
        self,
        id: str,
        distance_km: float,
        from_address: str,
        to_address: str,
        total: float,
        date: str,
    ):
        self.id = id
        self.service = TransportServiceType.BOLT
        self.distance_km = distance_km
        self.from_address = from_address
        self.to_address = to_address
        self.total_euros = total
        self.date = date


@dataclass
class UberTransportationExpense(TransportationExpense):
    def __init__(
        self,
        id: str,
        distance_km: float,
        from_address: str,
        to_address: str,
        total: float,
        date: str,
    ):
        self.id = id
        self.service = TransportServiceType.UBER
        self.distance_km = distance_km
        self.from_address = from_address
        self.to_address = to_address
        self.total_euros = total
        self.date = date

    def same_expense(self, other_expense: "UberTransportationExpense") -> bool:
        return (
            self.distance_km == other_expense.distance_km
            and self.from_address == other_expense.from_address
            and self.to_address == other_expense.to_address
            and self.total_euros == other_expense.total_euros
            and self.date == other_expense.date
        )
