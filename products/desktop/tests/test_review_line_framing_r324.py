"""R324: exact journal framing in the premium source-bound read path."""
import unittest

from fvs_suite.review_line_framing_r324 import (
    MAX_EVENTS, MAX_JOURNAL_BYTES, canonical_review_records,
)


class ReviewLineFramingR324(unittest.TestCase):
    def hold(self, raw):
        with self.assertRaisesRegex(ValueError, "noncanonical record boundaries"):
            canonical_review_records(raw)

    def test_empty_journal(self):
        self.assertEqual(canonical_review_records(b""), ())

    def test_lf(self):
        self.assertEqual(canonical_review_records(b'{}\n'), (b"{}",))

    def test_crlf(self):
        self.assertEqual(canonical_review_records(b'{}\r\n'), (b"{}",))

    def test_mixed_lf_crlf(self):
        self.assertEqual(canonical_review_records(b'{}\r\n{"b":2}\n'),
                         (b"{}", b'{"b":2}'))

    def test_escaped_cr_string_is_not_separator(self):
        self.assertEqual(canonical_review_records(b'{"a":"\\r"}\n'),
                         (b'{"a":"\\r"}',))

    def test_multilingual_bytes_are_preserved(self):
        raw = '{"a":"漢字☃"}\n'.encode()
        self.assertEqual(canonical_review_records(raw), (raw[:-1],))

    def test_unterminated_record_hold(self):
        self.hold(b"{}")

    def test_bare_cr_between_valid_objects_hold(self):
        self.hold(b'{}\r{}\n')

    def test_bare_cr_at_start_hold(self):
        self.hold(b'\r{}\n')

    def test_bare_cr_in_json_whitespace_hold(self):
        self.hold(b'{"a":\r1}\n')

    def test_double_cr_before_lf_hold(self):
        self.hold(b'{}\r\r\n')

    def test_vertical_tab_record_boundary_hold(self):
        self.hold(b'{}\x0b{}\n')

    def test_form_feed_record_boundary_hold(self):
        self.hold(b'{}\x0c{}\n')

    def test_nul_hold(self):
        self.hold(b'{"a":"\x00"}\n')

    def test_leading_blank_hold(self):
        self.hold(b'\n{}\n')

    def test_trailing_blank_hold(self):
        self.hold(b'{}\n\n')

    def test_empty_crlf_hold(self):
        self.hold(b'\r\n')

    def test_non_bytes_hold(self):
        for value in (None, "{}\n", bytearray(b"{}\n"), memoryview(b"{}\n")):
            with self.subTest(value=type(value).__name__):
                self.hold(value)

    def test_event_limit_exact(self):
        self.assertEqual(len(canonical_review_records(b'{}\n' * MAX_EVENTS)), MAX_EVENTS)

    def test_event_limit_over_hold(self):
        self.hold(b'{}\n' * (MAX_EVENTS + 1))

    def test_byte_limit_over_hold(self):
        self.hold(b'{}\n' * (MAX_JOURNAL_BYTES // 3 + 1))

    def test_previous_splitlines_would_accept_bare_cr(self):
        raw = b'{}\r{}\n'
        self.assertEqual(raw.splitlines(), [b"{}", b"{}"])
        self.hold(raw)

    def test_control_vt_rejected_even_if_splitlines_keeps_it(self):
        raw = b'{}\x0b{}\n'
        self.assertEqual(raw.splitlines(), [b"{}\x0b{}"])
        self.hold(raw)


if __name__ == "__main__":
    unittest.main()
