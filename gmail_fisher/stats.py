import collections
import logging
from typing import List

import matplotlib.pyplot as plt

from .gmail_gateway import GmailGateway
from .models import GmailMessage


def plot_uber_eats_expenses(sender_email, keywords):
    gmail_messages = GmailGateway.run_batch_get_message_detail(
        sender_emails=sender_email, keywords=keywords, max_results=1000
    )
    stats = get_uber_eats_stats(gmail_messages)
    sorted_timeline_totals = get_sorted_dict(stats["timeline_totals"])
    draw_bar_plot(sorted_timeline_totals, stats["total_payed"])


def get_uber_eats_stats(gmail_messages: List[GmailMessage]) -> dict:
    timeline_payed = dict()
    for message in gmail_messages:
        logging.info(
            f"Processing message with id='{message.id}', subject='{message.subject}'"
        )

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


def get_sorted_dict(dictionary: dict) -> dict:
    sorted_dict = collections.OrderedDict()
    for key in sorted(dictionary.keys()):
        sorted_dict.update({key: dictionary[key]})

    return sorted_dict


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
