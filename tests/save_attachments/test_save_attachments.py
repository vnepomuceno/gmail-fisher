import unittest
from gmail_fisher.save_attachments.save_attachments import get_payslip_filename


class TestSaveAttachments(unittest.TestCase):
    def test_health_check(self):
        self.assertEqual(True, True)

    def test_get_payslip_filename(self):
        subject = 'Please note that the Payslip for the income earned in 8-2020 is attached.'
        expected = 'PaySlip_2020-8.pdf'
        filename = get_payslip_filename(subject)

        assert filename == expected


if __name__ == '__main__':
    unittest.main()
