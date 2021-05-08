import unittest
from typing import Iterable
from unittest import mock

from gmail_fisher.gmail_gateway import GmailGateway
from gmail_fisher.models import GmailMessage


class TestGmailGateway(unittest.TestCase):
    def test_health_check(self):
        self.assertEqual(True, True)

    @mock.patch("gmail_fisher.gmail_gateway.Resource")
    def test_run_batch_get_message_detail(self, client):
        messages: Iterable[GmailMessage] = GmailGateway.run_batch_get_message_detail(
            sender_emails="uber.portugal@uber.com",
            keywords="Total",
            max_results=50,
            fetch_body=True,
        )
        assert len(messages) == 50
        for message in messages:
            self.assertFalse(not message.id)
            self.assertFalse(not message.date)
            self.assertFalse(not message.subject)
            self.assertFalse(not message.body)


if __name__ == "__main__":
    unittest.main()
