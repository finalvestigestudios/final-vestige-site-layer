"""R321 local synthetic JSONL structural tests, no encrypted/customer records."""
from __future__ import annotations

import unittest

from scripts.verify_restored_bundle_r320 import (ERROR, MAX_EVENTS,
                                                _verify_journal_structure)


class RestoredJournalStructureR321(unittest.TestCase):
    def hold(self, data, count):
        with self.assertRaises(ValueError) as caught:
            _verify_journal_structure(data, count)
        self.assertEqual(str(caught.exception), ERROR)

    def test_empty_journal_matches_zero(self):
        self.assertEqual(_verify_journal_structure(b"", 0), 0)

    def test_single_and_multiple_records(self):
        self.assertEqual(_verify_journal_structure(b'{"synthetic":true}\n', 1), 1)
        self.assertEqual(_verify_journal_structure(b'{"a":1}\n{"b":2}\n', 2), 2)

    def test_crlf_accepts_same_as_premium_reader(self):
        self.assertEqual(_verify_journal_structure(b'{"a":1}\r\n', 1), 1)

    def test_declared_count_too_small(self):
        self.hold(b'{"a":1}\n', 0)

    def test_declared_count_too_large(self):
        self.hold(b'{"a":1}\n', 2)

    def test_missing_final_newline(self):
        self.hold(b'{"a":1}', 1)

    def test_blank_record(self):
        self.hold(b'{"a":1}\n\n', 2)

    def test_malformed_json(self):
        self.hold(b'{"a":\n', 1)

    def test_array_is_not_event(self):
        self.hold(b'[1,2]\n', 1)

    def test_duplicate_event_keys(self):
        self.hold(b'{"a":1,"a":2}\n', 1)

    def test_nonfinite_json(self):
        for raw in (b'NaN', b'Infinity', b'-Infinity'):
            with self.subTest(raw=raw):
                self.hold(b'{"a":' + raw + b'}\n', 1)

    def test_bad_unicode(self):
        self.hold(b'{"x":"\xff"}\n', 1)

    def test_nul(self):
        self.hold(b'{"a":"\x00"}\n', 1)

    def test_count_requires_int_not_bool(self):
        for bad in (True, False, 1.0, "1", -1, MAX_EVENTS + 1):
            with self.subTest(value=bad):
                self.hold(b'{"a":1}\n', bad)

    def test_bytes_only(self):
        self.hold('{"a":1}\n', 1)

    def test_too_many_records(self):
        self.hold(b'{}\n' * (MAX_EVENTS + 1), MAX_EVENTS)


if __name__ == "__main__":
    unittest.main()
