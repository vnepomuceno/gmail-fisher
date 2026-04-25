import sys
from pathlib import Path

import click
from rich.panel import Panel

from gmail_fisher import console, get_logger
from gmail_fisher.data.models import FoodServiceType, TransportServiceType
from gmail_fisher.services.attachments import export_email_attachments
from gmail_fisher.services.bank import export_bank_expenses
from gmail_fisher.services.food import export_food_expenses
from gmail_fisher.services.messages import list_email_messages
from gmail_fisher.services.transport import export_transport_expenses

logger = get_logger(__name__)


def _print_banner(description: str):
    console.print(
        Panel(
            f"[bold cyan]Gmail Fisher[/bold cyan]\n[dim]{description}[/dim]",
            border_style="cyan",
            expand=False,
            padding=(0, 2),
        )
    )
    console.print()


@click.command()
@click.option("--sender-email", help="Sender email to filter messages")
@click.option("--keywords", help="Keywords to filter messages")
def save_attachments_command(sender_email: str, keywords: str):
    _print_banner("Save email attachments")
    export_email_attachments(sender_email, keywords)


@click.command()
@click.option("--output-filepath", help="Output JSON file path")
def export_uber_eats_expenses_command(output_filepath: str):
    _print_banner("Export Uber Eats expenses")
    export_food_expenses(FoodServiceType.UBER_EATS, output_filepath)


@click.command()
@click.option("--output-filepath", help="Output JSON file path")
def export_bolt_food_expenses_command(output_filepath: str):
    _print_banner("Export Bolt Food expenses")
    export_food_expenses(FoodServiceType.BOLT_FOOD, output_filepath)


@click.command()
@click.option("--output-filepath", help="Output JSON file path")
def export_food_expenses_command(output_filepath: str):
    _print_banner("Export all food expenses")
    export_food_expenses(FoodServiceType.ALL, Path(output_filepath), upload_s3=True)


@click.command()
@click.option("--output-filepath", help="Output JSON file path")
def export_bank_expenses_command(output_filepath: str):
    _print_banner("Export bank expenses")
    export_bank_expenses(Path(output_filepath), upload_s3=True)


@click.command()
@click.option("--output-filepath", help="Output JSON file path")
def export_transport_expenses_command(output_filepath: str):
    _print_banner("Export transport expenses")
    export_transport_expenses(Path(output_filepath), upload_s3=True)


@click.command()
@click.option("--sender-email", help="Sender email to filter messages")
@click.option("--keywords", help="Keywords to filter messages")
def list_messages_command(sender_email: str, keywords: str):
    _print_banner("List email messages")
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
        export_food_expenses(FoodServiceType.ALL, Path(sys.argv[2]), upload_s3=True)
    elif script == "export_bank_expenses":
        export_bank_expenses(Path(sys.argv[2]))
    elif script == "export_transport_expenses":
        export_transport_expenses(output_path=sys.argv[2])
    elif script == "list_messages":
        list_email_messages(sys.argv[2], sys.argv[3])
    else:
        raise NotImplemented
