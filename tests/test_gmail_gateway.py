import datetime
import unittest

from gmail_fisher.models import GmailMessage
from gmail_fisher.gmail_gateway import FileUtils


class TestGmailGateway(unittest.TestCase):
    def test_health_check(self):
        self.assertEqual(True, True)

    def test_get_date_as_datetime(self):
        message = GmailMessage(
            id="id",
            subject="subject",
            user_id="me",
            date="Sun, 29 Nov 2020 21:32:07 +0000 (UTC)",
            attachments=list(),
        )
        expected = datetime.datetime(2020, 11, 29)
        result = message.get_date_as_datetime()
        assert result == expected

    def test_get_payslip_filename(self):
        subject = (
            "Please note that the Payslip for the income earned in 8-2020 is attached."
        )
        expected = "PaySlip_2020-8.pdf"
        filename = FileUtils.get_payslip_filename(subject)

        assert filename == expected


if __name__ == "__main__":
    unittest.main()
