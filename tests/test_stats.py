import unittest

from gmail_fisher.stats import get_arguments


class TestStats(unittest.TestCase):
    def test_health_check(self):
        self.assertEqual(True, True)

    def test_get_arguments(self):
        expected = dict(sender_emails='uber.portugal@uber.com', keywords='Total')
        args = get_arguments(['run.py', 'stats', 'uber.portugal@uber.com', 'Total'])
        assert args == expected


if __name__ == '__main__':
    unittest.main()
