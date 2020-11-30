print('__file__={0:<35} | __name__={1:<20} | __package__={2:<20}'.format(__file__, __name__, str(__package__)))
import datetime
import re
import sys
from dataclasses import dataclass
from typing import List

import matplotlib.pyplot as plt
from .authenticate import authenticate_gmail_api
from googleapiclient.discovery import build


@dataclass
class GmailMessage:
    id: str
    subject: str
    user_id: str
    date: datetime

    def get_total_payed(self) -> float:
        try:
            match = re.search("[€][1-9]?[0-9].[0-9][0-9]", self.subject).group(0)
        except AttributeError:
            print(f"⚠️  Could not match total payed (e.g. €12.30) for message id='{self.id}'")
            return 0
        return float(match.strip('€'))

    def ignore_message(self) -> bool:
        if 'Refund' in self.subject or self.get_total_payed() == 0:
            return True
        else:
            return False


def plot_uber_eats_expenses(argv):
    args = get_arguments(argv)
    credentials = authenticate_gmail_api()
    gmail_messages = get_gmail_filtered_messages(credentials, args)
    stats = get_uber_eats_stats(gmail_messages)
    draw_bar_plot(stats['timeline_totals'], stats['total_payed'])


def get_uber_eats_stats(gmail_messages: List[GmailMessage]) -> dict:
    timeline_payed = dict()
    for message in gmail_messages:
        print(f"Processing id={message.id}, subject='{message.subject}'")

        if message.ignore_message():
            print(f"⚠️  Message ignored with subject='{message.subject}'\n---------------")
            continue

        total = message.get_total_payed()
        date = message.date
        date_label = date.strftime('%Y-%m')

        if timeline_payed.keys().__contains__(date_label):
            total_list = timeline_payed[date_label]
            total_list.append(total)
            timeline_payed.update({date_label: total_list})
        else:
            timeline_payed.update({date_label: [total]})

        print(f"✅  Total payed is €{total} in {date}")
        print("---------------")

    total_payed = 0
    timeline_totals = dict()
    for item in timeline_payed.items():
        month_total = sum(item[1])
        timeline_totals.update({item[0]: month_total})
        total_payed += month_total

    print('\n\n====================\n')
    print(f"💸  MONTHLY EXPENSE OCCURRENCES: {timeline_payed}\n\n====================\n")
    print(f"💸  MONTHLY TOTALS: {timeline_totals}\n\n====================\n")
    print(f"💸  TOTAL PAYED EVER: {round(total_payed, 2)}€\n\n====================")

    return dict(timeline_payed=timeline_payed, timeline_totals=timeline_totals, total_payed=round(total_payed, 2))


def get_gmail_filtered_messages(credentials, args):
    service = build('gmail', 'v1', credentials=credentials)

    list_message_results = service.users().messages().list(
        userId='me',
        q=f"from:{args['sender_emails']} {args['keywords']}",
        maxResults=1000
    ).execute()

    if list_message_results['resultSizeEstimate'] == 0:
        print('No messages found.')
        sys.exit(0)

    message_list = list()
    for message in list_message_results['messages']:
        get_message_result = service.users().messages().get(id=message['id'], userId="me").execute()
        message = GmailMessage(
            id=message['id'],
            subject=get_message_result['snippet'],
            user_id='me',
            date=get_date(
                next(item for item in get_message_result['payload']['headers'] if item["name"] == "Date")['value']
            )
        )
        print(f"Fetched message from date='{message.date.strftime('%Y-%m-%d')}', "
              f"subject='{message.subject[0:120]} ...'")
        message_list.append(message)

    return message_list


def get_date(date_str) -> datetime:
    """
    Receives a string date in the format 'Sun, 29 Nov 2020 21:32:07 +0000 (UTC)',
    and returns a datetime with precision up to the day.
    """
    date_arr = date_str.strip(' +0000 (UTC)') \
        .split(', ')[1] \
        .split(' ')
    date_str = f"{date_arr[0]} {date_arr[1]} {date_arr[2]}"
    date = datetime.datetime.now()
    try:
        date = datetime.datetime.strptime(date_str, '%d %b %Y')
    except ValueError as ve:
        print(f"⚠️  Date could not be parsed '{date_str}'. Raised error {ve}")

    return date


def get_arguments(argv) -> dict:
    """
    Receives sys.argv as argument and returns a dictionary of `sender_emails` and `keywords`,
    or exits the program if those two arguments are not provided
    """
    try:
        sender_emails = argv[2].strip('\'')
        keywords = argv[3].strip('\'')
        print(f"Stats script with sender_emails='{sender_emails}' and keywords='{keywords}' 📈")
        return dict(sender_emails=sender_emails, keywords=keywords)
    except IndexError:
        print(f"❌  Could not parse arguments $1=sender_emails, $2=keywords")
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
    plt.ylabel('Euros €')
    plt.xticks(rotation=45)
    plt.show()
