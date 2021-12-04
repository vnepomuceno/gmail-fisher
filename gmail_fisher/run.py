import sys

import click

from gmail_fisher.models import FoodServiceType, TransportServiceType
from gmail_fisher.services import (
    export_email_attachments,
    export_food_expenses,
    export_transport_expenses,
    list_email_messages,
)
from gmail_fisher.utils import get_logger

logger = get_logger(__name__)


@click.command()
@click.option("--sender-email", help="Sender email to filter messages")
@click.option("--keywords", help="Keywords to filter messages")
def save_attachments_command(sender_email: str, keywords: str):
    export_email_attachments(sender_email, keywords)


@click.command()
@click.option("--output-filepath", help="File path of the output")
def export_uber_eats_expenses_command(output_filepath: str):
    export_food_expenses(FoodServiceType.UBER_EATS, output_filepath)


@click.command()
@click.option("--output-filepath", help="File path of the output")
def export_bolt_food_expenses_command(output_filepath: str):
    export_food_expenses(FoodServiceType.BOLT_FOOD, output_filepath)


@click.command()
@click.option("--output-filepath", help="File path of the output")
def export_food_expenses_command(output_filepath: str):
    export_food_expenses(FoodServiceType.ALL, output_filepath)


@click.command()
@click.option("--output-filepath", help="File path of the output")
def export_transport_expenses_command(output_filepath: str):
    export_transport_expenses(TransportServiceType.BOLT, output_filepath)


@click.command()
@click.option("--sender-email", help="Sender email to filter messages")
@click.option("--keywords", help="Keywords to filter messages")
def list_messages_command(sender_email: str, keywords: str):
    list_email_messages(sender_email, keywords)


if __name__ == "__main__":
    script = sys.argv[1]
    if script == "save_attachments":
        export_email_attachments(sys.argv[2], sys.argv[3])
    elif script == "export_uber_eats_expenses":
        export_food_expenses(FoodServiceType.UBER_EATS, sys.argv[2])
    elif script == "export_bolt_food_expenses":
        export_food_expenses(FoodServiceType.BOLT_FOOD, sys.argv[2])
    elif script == "export_food_expenses":
        export_food_expenses(FoodServiceType.ALL, sys.argv[2])
    elif script == "export_transport_expenses":
        export_transport_expenses(TransportServiceType.BOLT, sys.argv[2])
    elif script == "list_messages":
        list_email_messages(sys.argv[2], sys.argv[3])
    else:
        raise NotImplemented
