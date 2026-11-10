"""R323: private offline JSONL record-boundary and numeric/text guards."""
import unittest
from scripts.verify_restored_bundle_r320 import (
    ERROR, MAX_EVENTS, _verify_journal_structure,
)

class RestoredJournalCanonicalR323(unittest.TestCase):
    def hold(self, raw, count=1):
        with self.assertRaises(ValueError) as caught:
            _verify_journal_structure(raw, count)
        self.assertEqual(str(caught.exception), ERROR)
        self.assertTrue(caught.exception.__context__ is None or caught.exception.__suppress_context__)

    def test_empty_journal_count_zero(self):
        self.assertEqual(_verify_journal_structure(b"", 0), 0)

    def test_single_lf_record(self):
        self.assertEqual(_verify_journal_structure(b'{"a":1}\n', 1), 1)

    def test_multiple_lf_records(self):
        self.assertEqual(_verify_journal_structure(b'{"a":1}\n{"b":2}\n', 2), 2)

    def test_single_crlf_record(self):
        self.assertEqual(_verify_journal_structure(b'{"a":1}\r\n', 1), 1)

    def test_mixed_crlf_and_lf(self):
        self.assertEqual(_verify_journal_structure(b'{}\r\n{}\n', 2), 2)

    def test_bare_cr_record_separator_hold(self):
        self.hold(b'{}\r{}\n', 2)

    def test_cr_inside_json_whitespace_hold(self):
        self.hold(b'{"a":\r1}\n')

    def test_cr_at_start_hold(self):
        self.hold(b'\r{}\n')

    def test_double_crlf_hold(self):
        self.hold(b'{}\r\r\n')

    def test_unterminated_hold(self):
        self.hold(b'{}')

    def test_blank_lf_hold(self):
        self.hold(b'{}\n\n', 2)

    def test_blank_crlf_hold(self):
        self.hold(b'{}\r\n\r\n', 2)

    def test_simple_float_hold(self):
        self.hold(b'{"a":1.5}\n')

    def test_exponent_float_hold(self):
        self.hold(b'{"a":1e309}\n')

    def test_subnormal_float_hold(self):
        self.hold(b'{"a":1e-900}\n')

    def test_nested_float_hold(self):
        self.hold(b'{"a":[{"b":0.125}]}\n')

    def test_json_constant_hold(self):
        self.hold(b'{"a":NaN}\n')

    def test_escaped_surrogate_value_hold(self):
        self.hold(b'{"a":"\\ud800"}\n')

    def test_escaped_surrogate_key_hold(self):
        self.hold(b'{"\\udfff":true}\n')

    def test_nested_escaped_surrogate_hold(self):
        self.hold(b'{"a":["\\udc00"]}\n')

    def test_valid_unicode_scalar_pass(self):
        self.assertEqual(_verify_journal_structure('{"r":"漢字🚀"}\n'.encode(), 1), 1)

    def test_valid_escaped_unicode_pass(self):
        self.assertEqual(_verify_journal_structure(b'{"r":"\\u00e9"}\n', 1), 1)

    def test_valid_json_string_escaped_carriage_return_pass(self):
        self.assertEqual(_verify_journal_structure(b'{"r":"\\r"}\n', 1), 1)

    def test_duplicate_key_hold(self):
        self.hold(b'{"a":1,"a":2}\n')

    def test_non_object_hold(self):
        self.hold(b'[]\n')

    def test_count_mismatch_hold(self):
        self.hold(b'{}\n', 2)

    def test_count_type_hold(self):
        self.hold(b'{}\n', True)

    def test_count_limit_hold(self):
        self.hold(b'{}\n', MAX_EVENTS+1)

    def test_invalid_utf8_hold(self):
        self.hold(b'{"a":"\xff"}\n')

    def test_original_str_input_hold(self):
        self.hold('{}\n')

if __name__ == '__main__':
    unittest.main()
