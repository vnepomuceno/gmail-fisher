import collections
import datetime
import json
import os
import sys
from dataclasses import dataclass
from typing import List

import matplotlib.pyplot as plt

from .gmail_gateway import GmailMessage
from .gmail_gateway import authenticate
from .gmail_gateway import get_filtered_messages
from .log import info, error, success


@dataclass
class UberEatsExpense:
    restaurant: str
    total: float
    date: datetime


def plot_uber_eats_expenses(argv):
    args = get_arguments(argv)
    credentials = authenticate()
    gmail_messages = get_filtered_messages(
        credentials, args["sender_emails"], args["keywords"], 1000, False
    )
    stats = get_uber_eats_stats(gmail_messages)
    sorted_timeline_totals = get_sorted_dict(stats["timeline_totals"])
    draw_bar_plot(sorted_timeline_totals, stats["total_payed"])


def save_uber_eats_expenses(argv):
    filepath = argv[2]
    credentials = authenticate()
    gmail_messages = get_filtered_messages(
        credentials, "uber.portugal@uber.com", "Total", 1000, False
    )
    expenses = get_uber_eats_expenses(gmail_messages)
    json_expenses = serialize_expenses_to_json_file(expenses, filepath)
    success(
        "Successfully written expenses to json file",
        {"file": filepath, "json": json_expenses},
    )


def get_uber_eats_stats(gmail_messages: List[GmailMessage]) -> dict:
    timeline_payed = dict()
    for message in gmail_messages:
        info("Processing message", {"id": message.id, "subject": message.subject})

        if message.ignore_message():
            print(
                f"⚠️  Message ignored with subject='{message.subject}'\n---------------"
            )
            continue

        total = message.get_total_payed_from_subject()
        date_label = message.get_date_as_datetime().strftime("%Y-%m")

        if timeline_payed.keys().__contains__(date_label):
            total_list = timeline_payed[date_label]
            total_list.append(total)
            timeline_payed.update({date_label: total_list})
        else:
            timeline_payed.update({date_label: [total]})

        print(f"✅  Total payed is €{total} in {date_label}")
        print("---------------")

    total_payed = 0
    timeline_totals = dict()
    for item in timeline_payed.items():
        month_total = sum(item[1])
        timeline_totals.update({item[0]: month_total})
        total_payed += month_total

    print("\n\n====================\n")
    print(f"💸  MONTHLY EXPENSE OCCURRENCES: {timeline_payed}\n\n====================\n")
    print(f"💸  MONTHLY TOTALS: {timeline_totals}\n\n====================\n")
    print(f"💸  TOTAL PAYED EVER: {round(total_payed, 2)}€\n\n====================")

    return dict(
        timeline_payed=timeline_payed,
        timeline_totals=timeline_totals,
        total_payed=round(total_payed, 2),
    )


def get_uber_eats_expenses(gmail_messages: List[GmailMessage]) -> [UberEatsExpense]:
    expenses = []
    for message in gmail_messages:
        try:
            expenses.append(
                UberEatsExpense(
                    restaurant=message.subject.split("receipt for ")[1]
                    .split(".")[0]
                    .replace("&#39;", "'")
                    .replace("&amp;", "&")
                    .replace("\u00ae", "")
                    .replace(" 🐠", "")
                    .replace(" (Marquês de Pombal)", "")
                    .replace("® (Saldanha)", "")
                    .replace(" (Saldanha)", "")
                    .replace(" (General Roçadas)", "")
                    .replace(" (Fontes Pereira de Melo)", "")
                    .replace(" (São Sebastião)", "")
                    .replace(" (Graça)", "")
                    .replace(" (Monumental)", "")
                    .replace(" (Saldanha Residence)", "")
                    .replace(" (República)", "")
                    .replace(" (Sta", "")
                    .replace(" (Barata Salgueiro)", "")
                    .replace(" (Rossio)", ""),
                    total=float(message.subject.split(" ")[1].replace("€", "")),
                    date=message.get_date_as_datetime().date().__str__(),
                )
            )
        except IndexError:
            error(
                "Error fetching UberEats expense from email message",
                {"subject": message.subject},
            )

    return expenses


def serialize_expenses_to_json_file(expenses: [UberEatsExpense], json_filepath) -> str:
    file = open(json_filepath, "w")
    json_expenses = json.dumps([expense.__dict__ for expense in expenses])
    file.write(json_expenses)
    file.close()
    return json_expenses


def get_sorted_dict(dictionary: dict) -> dict:
    sorted_dict = collections.OrderedDict()
    for key in sorted(dictionary.keys()):
        sorted_dict.update({key: dictionary[key]})

    return sorted_dict


def get_arguments(argv) -> dict:
    """
    Receives sys.argv as argument and returns a dictionary of `sender_emails` and `keywords`,
    or exits the program if those two arguments are not provided
    """
    try:
        sender_emails = argv[2].strip("'")
        keywords = argv[3].strip("'")
        print(
            f"Stats script with sender_emails='{sender_emails}' and keywords='{keywords}' 📈"
        )
        return dict(sender_emails=sender_emails, keywords=keywords)
    except IndexError:
        print("❌  Could not parse arguments $1=sender_emails, $2=keywords")
        sys.exit(1)


def draw_bar_plot(months_totals: dict, total_payed: float):
    """
    Receives as arguments:
        - Dictionary of `months_totals` with keys as dates in format '2020-11' and
        values the total payed for that month as a float.
        (e.g. {'2020-11': 57.20, '2020-10': 123.10})
        - Total payed since the beginning as a float
    And draws a bar plot with the total payed for each month. In the title it is
    displayed the total payed since the beginning.
    """
    plt.bar(months_totals.keys(), months_totals.values())
    plt.title(f"UberEats Total Spent: {total_payed}€")
    plt.ylabel("Euros €")
    plt.xticks(rotation=60)
    plt.show()
