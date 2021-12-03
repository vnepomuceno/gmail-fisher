import sys

import click

from gmail_fisher import services
from gmail_fisher.parsers.food import (
    UberEatsParser,
    BoltFoodParser,
    FoodExpenseParser,
)
from gmail_fisher.parsers.transportation import BoltParser
from gmail_fisher.services import gmail_save_attachments
from gmail_fisher.utils import get_logger

logger = get_logger(__name__)


@click.command()
@click.option("--sender-email", help="Sender email to filter messages")
@click.option("--keywords", help="Keywords to filter messages")
def save_attachments_command(sender_email, keywords):
    logger.info(
        f"Running save_attachments with sender_email='{sender_email}', keywords='{keywords}'"
    )
    gmail_save_attachments(sender_email=sender_email, keywords=keywords)


@click.command()
@click.option("--output-filepath", help="File path of the output")
def export_uber_eats_expenses_command(output_filepath):
    logger.info(
        f"Running export_uber_eats_expenses with output_filepath='{output_filepath}'"
    )
    FoodExpenseParser.serialize_expenses_to_json_file(
        expenses=UberEatsParser.fetch_expenses(), json_filepath=output_filepath
    )


@click.command()
@click.option("--output-filepath", help="File path of the output")
def export_bolt_food_expenses_command(output_filepath):
    logger.info(
        f"Running export_bolt_food_expenses with output_filepath='{output_filepath}'"
    )
    FoodExpenseParser.serialize_expenses_to_json_file(
        expenses=BoltFoodParser.fetch_expenses(), json_filepath=output_filepath
    )


@click.command()
@click.option("--output-filepath", help="File path of the output")
def export_food_expenses_command(output_filepath):
    logger.info(
        f"Running export_food_expenses with output_filepath='{output_filepath}'"
    )
    food_expenses = list(UberEatsParser.fetch_expenses()) + list(
        BoltFoodParser.fetch_expenses()
    )
    FoodExpenseParser.serialize_expenses_to_json_file(
        expenses=food_expenses, json_filepath=output_filepath
    )


@click.command()
@click.option("--output-filepath", help="File path of the output")
def export_transport_expenses_command(output_filepath):
    logger.info(
        f"Running export_transport_expenses with output_filepath='{output_filepath}'"
    )
    transport_expenses = list(BoltParser.fetch_expenses())
    BoltParser.serialize_expenses_to_json_file(
        expenses=transport_expenses, json_filepath=output_filepath
    )


@click.command()
@click.option("--sender-email", help="Sender email to filter messages")
@click.option("--keywords", help="Keywords to filter messages")
def list_messages_command(sender_email, keywords):
    logger.info(
        f"Running list_messages with sender_email='{sender_email}', keywords='{keywords}'"
    )
    services.get_email_messages(
        sender_emails=sender_email, keywords=keywords, max_results=1000
    )


if __name__ == "__main__":
    script = sys.argv[1]
    if script == "save_attachments":
        gmail_save_attachments(sender_email=sys.argv[2], keywords=sys.argv[3])
    elif script == "export_uber_eats_expenses":
        FoodExpenseParser.serialize_expenses_to_json_file(
            expenses=UberEatsParser.fetch_expenses(), json_filepath=sys.argv[2]
        )
    elif script == "export_bolt_food_expenses":
        FoodExpenseParser.serialize_expenses_to_json_file(
            expenses=BoltFoodParser.fetch_expenses(), json_filepath=sys.argv[2]
        )
    elif script == "export_food_expenses":
        food_expenses = list(UberEatsParser.fetch_expenses()) + list(
            BoltFoodParser.fetch_expenses()
        )
        FoodExpenseParser.serialize_expenses_to_json_file(
            expenses=food_expenses, json_filepath=sys.argv[2]
        )
        logger.info("FOOD EXPENSES: " + food_expenses)
    elif script == "export_transport_expenses":
        transport_expenses = list(BoltParser.fetch_expenses())
        BoltParser.serialize_expenses_to_json_file(
            expenses=transport_expenses, json_filepath=sys.argv[2]
        )
        logger.info(f"TRANSPORT EXPENSES: {transport_expenses}")
    elif script == "list_messages":
        services.get_email_messages(
            sender_emails=sys.argv[2], keywords=sys.argv[3], max_results=1000
        )
    else:
        raise NotImplemented
