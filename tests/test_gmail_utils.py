import datetime
import unittest

from gmail_fisher.gmail_gateway import get_date


class TestGmailUtils(unittest.TestCase):
    def test_health_check(self):
        self.assertEqual(True, True)

    def test_get_date(self):
        expected = datetime.datetime(2020, 11, 29)
        date = get_date('Sun, 29 Nov 2020 21:32:07 +0000 (UTC)')
        assert date == expected


if __name__ == '__main__':
    unittest.main()
