"""Run with: python -m unittest -v"""

import unittest

from collector import filter_records, is_public_ip, parse_powershell_json


class TestIsPublicIp(unittest.TestCase):
    def test_public_addresses(self):
        self.assertTrue(is_public_ip("8.8.8.8"))
        self.assertTrue(is_public_ip("2607:f8b0:4006:81f::2004"))

    def test_non_public_addresses(self):
        for ip in ["10.0.0.1", "172.16.5.4", "192.168.1.1", "127.0.0.1",
                   "169.254.1.1", "::1", "fe80::1", "0.0.0.0"]:
            self.assertFalse(is_public_ip(ip), ip)

    def test_not_an_ip(self):
        self.assertFalse(is_public_ip("something.edgekey.net"))
        self.assertFalse(is_public_ip(""))


class TestParsePowershellJson(unittest.TestCase):
    def test_empty_output(self):
        self.assertEqual(parse_powershell_json("  \n"), [])

    def test_single_entry_becomes_list(self):
        result = parse_powershell_json('{"Entry": "a.com", "Data": "1.1.1.1", "Type": 1}')
        self.assertEqual(len(result), 1)


class TestFilterRecords(unittest.TestCase):
    def test_keeps_only_public_a_and_aaaa(self):
        raw = [
            {"Entry": "good.com", "Data": "1.1.1.1", "Type": 1, "TimeToLive": 60},
            {"Entry": "lan.home", "Data": "192.168.1.1", "Type": 1, "TimeToLive": 60},
            {"Entry": "alias.com", "Data": "cdn.example.net", "Type": 5, "TimeToLive": 60},
        ]
        records = filter_records(raw)
        self.assertEqual([r.domain for r in records], ["good.com"])

    def test_duplicates_removed_and_domain_normalized(self):
        raw = [
            {"Entry": "Example.COM.", "Data": "93.184.215.14", "Type": 1, "TimeToLive": 30},
            {"Entry": "example.com", "Data": "93.184.215.14", "Type": 1, "TimeToLive": 90},
        ]
        records = filter_records(raw)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].domain, "example.com")
        self.assertEqual(records[0].ttl, 90)


if __name__ == "__main__":
    unittest.main()
