import logging
import sys

import click

from gmail_fisher.save_attachments import gmail_save_attachments
from gmail_fisher.stats import plot_uber_eats_expenses
from gmail_fisher.stats import save_uber_eats_expenses
from gmail_fisher.gmail_gateway import GmailGateway


@click.command()
@click.option("--sender-email", help="Sender email to filter messages")
@click.option("--keywords", help="Keywords to filter messages")
def save_attachments_command(sender_email, keywords):
    logging.info(
        f"Running save_attachments with sender_email='{sender_email}', keywords='{keywords}'"
    )
    gmail_save_attachments(sender_email=sender_email, keywords=keywords)


@click.command()
@click.option("--sender-email", help="Sender email to filter messages")
@click.option("--keywords", help="Keywords to filter messages")
def uber_eats_stats_command(sender_email, keywords):
    logging.info(
        f"Running uber_eats_stats with sender_email='{sender_email}', keywords='{keywords}'"
    )
    plot_uber_eats_expenses(sender_email=sender_email, keywords=keywords)


@click.command()
@click.option("--output-filepath", help="File path of the output")
def uber_eats_save_expenses_command(output_filepath):
    logging.info(
        f"Running uber_eats_save_expenses with output_filepath='{output_filepath}'"
    )
    save_uber_eats_expenses(output_filepath=output_filepath)


@click.command()
@click.option("--sender-email", help="Sender email to filter messages")
@click.option("--keywords", help="Keywords to filter messages")
def list_messages_command(sender_email, keywords):
    logging.info(
        f"Running list_messages with sender_email='{sender_email}', keywords='{keywords}'"
    )
    GmailGateway.run_batch_get_message_detail(
        sender_emails=sender_email, keywords=keywords, max_results=1000
    )


if __name__ == "__main__":
    script = sys.argv[1]
    if script == "save_attachments":
        gmail_save_attachments(sender_email=sys.argv[2], keywords=sys.argv[3])
    elif script == "uber_eats_stats":
        plot_uber_eats_expenses(sender_email=sys.argv[2], keywords=sys.argv[3])
    elif script == "uber_eats_save_expenses":
        save_uber_eats_expenses(output_filepath=sys.argv[2])
    else:
        raise NotImplemented
