import unittest

from gmail_fisher.save_attachments import get_arguments
from gmail_fisher.save_attachments import get_payslip_filename


class TestSaveAttachments(unittest.TestCase):
    def test_health_check(self):
        self.assertEqual(True, True)

    def test_get_arguments_without_download(self):
        expected = dict(
            sender_emails="payroll.pt@my-company.com",
            keywords="payslip",
            download=False,
        )
        args = get_arguments(
            ["run.py", "save_attachments", "payroll.pt@my-company.com", "payslip"]
        )
        assert args == expected

    def test_get_arguments_with_download(self):
        expected = dict(
            sender_emails="payroll.pt@my-company.com", keywords="payslip", download=True
        )
        args = get_arguments(
            [
                "run.py",
                "save_attachments",
                "payroll.pt@my-company.com",
                "payslip",
                "--download-pdf",
            ]
        )
        assert args == expected

    def test_get_payslip_filename(self):
        subject = (
            "Please note that the Payslip for the income earned in 8-2020 is attached."
        )
        expected = "PaySlip_2020-8.pdf"
        filename = get_payslip_filename(subject)

        assert filename == expected


if __name__ == "__main__":
    unittest.main()
