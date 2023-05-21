import logging
from pathlib import Path
from typing import Iterable

from gmail_fisher.data.models import FoodExpense, FoodServiceType
from gmail_fisher.data.s3_uploader import S3BucketUploader
from gmail_fisher.parsers.food import BoltFoodParser, UberEatsParser, FoodExpenseParser

logger = logging.getLogger(__name__)


def get_food_expenses() -> Iterable[FoodExpense]:
    return list(BoltFoodParser.fetch_expenses()) + list(UberEatsParser.fetch_expenses())


def export_food_expenses(
    service_type: FoodServiceType,
    output_path: Path,
    upload_s3: bool = False,
    start_time: str = None,
    end_time: str = None,
):
    logger.info(f"Exporting food expenses with {service_type=}, {output_path=}")

    if service_type is FoodServiceType.UBER_EATS:
        FoodExpenseParser.serialize_expenses_to_json_file(
            expenses=UberEatsParser.fetch_expenses(start_time, end_time),
            output_path=str(output_path),
        )
    elif service_type is FoodServiceType.BOLT_FOOD:
        FoodExpenseParser.serialize_expenses_to_json_file(
            expenses=BoltFoodParser.fetch_expenses(start_time, end_time),
            output_path=str(output_path),
        )
    elif service_type is FoodServiceType.ALL:
        FoodExpenseParser.serialize_expenses_to_json_file(
            expenses=list(BoltFoodParser.fetch_expenses(start_time, end_time))
            + list(UberEatsParser.fetch_expenses(start_time, end_time)),
            output_path=str(output_path),
        )
    else:
        raise RuntimeError(f"Invalid food service type {service_type=}")

    if upload_s3:
        S3BucketUploader().upload(filepath=output_path, key=output_path.name)
