"""Run with: python -m unittest -v"""

import time
import unittest

from collector import DnsRecord
from storage import connect, count_records, get_all, save_records

GITHUB = DnsRecord("github.com", "140.82.112.4", "A", 60)
GOOGLE = DnsRecord("www.google.com", "142.250.80.36", "A", 60)


class TestStorage(unittest.TestCase):
    def setUp(self):
        # ":memory:" gives each test a fresh, temporary database
        self.conn = connect(":memory:")

    def tearDown(self):
        self.conn.close()

    def test_first_save_counts_all_as_new(self):
        self.assertEqual(save_records(self.conn, [GITHUB, GOOGLE]), 2)
        self.assertEqual(count_records(self.conn), 2)

    def test_second_save_counts_none_as_new(self):
        save_records(self.conn, [GITHUB, GOOGLE])
        self.assertEqual(save_records(self.conn, [GITHUB, GOOGLE]), 0)
        self.assertEqual(count_records(self.conn), 2)

    def test_only_new_records_counted(self):
        save_records(self.conn, [GITHUB])
        self.assertEqual(save_records(self.conn, [GITHUB, GOOGLE]), 1)

    def test_last_seen_updates_but_first_seen_stays(self):
        save_records(self.conn, [GITHUB])
        first = dict(get_all(self.conn)[0])
        time.sleep(1.1)  # timestamps are stored to the second
        save_records(self.conn, [GITHUB])
        second = dict(get_all(self.conn)[0])

        self.assertEqual(second["first_seen"], first["first_seen"])
        self.assertGreater(second["last_seen"], first["last_seen"])

    def test_empty_list(self):
        self.assertEqual(save_records(self.conn, []), 0)


if __name__ == "__main__":
    unittest.main()