"""R333: reject malformed premium review JSONL before any journal I/O.

All values are synthetic. These are helper tests, not a full repository test
run, Windows acceptance, a compliance decision or permission to release.
"""
from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from fvs_suite.journal_event_preflight_r333 import require_jsonl_object

PRIVATE = "PRIVATE_SYNTHETIC_BANK_ROW_333"
ERROR = "Review event must be one valid UTF-8 JSON object with unique keys"


class JournalEventPreflightR333(unittest.TestCase):
    def assert_rejected(self, payload):
        with self.assertRaises(ValueError) as seen:
            require_jsonl_object(payload)
        self.assertEqual(str(seen.exception), ERROR)
        self.assertIsNone(seen.exception.__cause__)
        self.assertIsNone(seen.exception.__context__)
        self.assertNotIn(PRIVATE, repr(seen.exception))

    def test_human_event_from_canonical_json_serializer(self):
        item = {"schema": 1, "reviewer": "human", "rationale": "synthetic review", "synthetic": True}
        require_jsonl_object(json.dumps(item, sort_keys=True, separators=(",", ":")).encode() + b"\n")

    def test_valid_empty_object(self):
        require_jsonl_object(b"{}\n")

    def test_valid_nested_object_and_array(self):
        require_jsonl_object(b'{"nested":{"source":1},"flags":[true,false,null]}\n')

    def test_valid_utf8_multilingual_review(self):
        require_jsonl_object('{"reviewer":"François 😀"}\n'.encode())

    def test_valid_high_exponent_number_is_not_binary_infinity(self):
        require_jsonl_object(b'{"synthetic_amount":1e9999}\n')

    def test_reject_duplicate_top_level_keys(self):
        self.assert_rejected(b'{"review":"one","review":"two"}\n')

    def test_reject_duplicate_nested_keys(self):
        self.assert_rejected(b'{"review":{"decision":"a","decision":"b"}}\n')

    def test_reject_non_object_array(self):
        self.assert_rejected(b'[1,2]\n')

    def test_reject_non_object_scalar(self):
        self.assert_rejected(b'"not an event"\n')

    def test_reject_json_null_root(self):
        self.assert_rejected(b'null\n')

    def test_reject_plaintext_record_that_legacy_writer_accepted(self):
        self.assert_rejected((PRIVATE + "\n").encode())

    def test_reject_invalid_utf8(self):
        self.assert_rejected(b'{"review":"\xff"}\n')

    def test_reject_unterminated_record(self):
        self.assert_rejected(b'{"review":1}')

    def test_reject_multiple_records(self):
        self.assert_rejected(b'{}\n{}\n')

    def test_reject_raw_carriage_return(self):
        self.assert_rejected(b'{"review":1}\r\n')

    def test_reject_nul(self):
        self.assert_rejected(b'{"review":1}\x00\n')

    def test_reject_nonfinite_numeric_constant(self):
        for literal in (b'NaN', b'Infinity', b'-Infinity'):
            with self.subTest(literal=literal):
                self.assert_rejected(b'{"amount":' + literal + b'}\n')

    def test_reject_trailing_junk(self):
        self.assert_rejected(b'{} ' + PRIVATE.encode() + b'\n')

    def test_reject_malformed_json_with_private_content(self):
        self.assert_rejected(b'{"' + PRIVATE.encode() + b'": }\n')

    def test_reject_parser_failure_without_exposing_context(self):
        with patch("fvs_suite.journal_event_preflight_r333.json.loads", side_effect=ValueError(PRIVATE)):
            self.assert_rejected(b'{"valid":"object"}\n')

    def test_reject_parser_recursion_failure(self):
        with patch("fvs_suite.journal_event_preflight_r333.json.loads", side_effect=RecursionError(PRIVATE)):
            self.assert_rejected(b'{"valid":"object"}\n')

    def test_reject_non_bytes(self):
        for value in ("{}\n", bytearray(b'{}\n'), None, memoryview(b'{}\n')):
            with self.subTest(value=type(value).__name__):
                self.assert_rejected(value)


if __name__ == "__main__":
    unittest.main()
