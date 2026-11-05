"""R199: native-source compatibility cues must obey physical UTF-8 file limits.

These direct-API tests exercise only source-custody staging; an NFKC cue is
human-review navigation, not a compliance/equivalence determination.
"""
import unittest

from fvs_suite.policy_compatibility_custody import owned_nfkc_hunks as stage

LIMIT = 10 * 1024 * 1024


def pair(before="Limit ⑩\n", after="Limit 10\n", *, number=3):
    return {"removed_sources": [(number, before)],
            "added_sources": [(number + 1, after)]}


class PhysicalUtf8SourceCustodyR199(unittest.TestCase):
    def test_valid_single_line_with_lf_and_nfk_cue(self):
        staged = stage([pair()])
        self.assertEqual(staged[0][1]["Limit 10\n"], [(3, "Limit ⑩\n")])

    def test_valid_windows_crlf(self):
        staged = stage([pair("Limit ⑩\r\n", "Limit 10\r\n")])
        self.assertEqual(staged[0][1]["Limit 10\r\n"], [(3, "Limit ⑩\r\n")])

    def test_valid_blank_physical_line(self):
        self.assertIsNotNone(stage([pair("\n", "\n")]))

    def test_valid_classic_mac_cr(self):
        self.assertIsNotNone(stage([pair("Limit ⑩\r", "Limit 10\r")]))

    def test_valid_unterminated_final_line(self):
        self.assertEqual(stage([pair("Limit ⑩", "Limit 10")])[0][2],
                         {"Limit 10": [(4, "Limit 10")]})

    def test_reject_lf_inside_a_claimed_physical_row(self):
        self.assertIsNone(stage([pair("Limit ⑩\nForged line ⑩\n")]))

    def test_reject_cr_inside_a_claimed_physical_row(self):
        self.assertIsNone(stage([pair("Limit ⑩\rForged line ⑩")]))

    def test_reject_lone_crlf_with_extra_second_line(self):
        self.assertIsNone(stage([pair("Limit ⑩\r\nExtra ⑩")]))

    def test_reject_other_unicode_line_breaks(self):
        for sep in ("\v", "\f", "\x1c", "\x85", "\u2028", "\u2029"):
            with self.subTest(codepoint=hex(ord(sep))):
                self.assertIsNone(stage([pair("Limit ⑩" + sep + "extra")]))

    def test_reject_empty_physical_line_source(self):
        self.assertIsNone(stage([pair("")]))

    def test_reject_unpaired_surrogates(self):
        for value in ("\ud800", "\udfff"):
            with self.subTest(value=repr(value)):
                self.assertIsNone(stage([pair("Limit ⑩" + value)]))

    def test_reject_non_ascii_two_byte_source_over_byte_limit(self):
        too_large_utf8 = "é" * (LIMIT // 2 + 1)
        self.assertLess(len(too_large_utf8), LIMIT)
        self.assertIsNone(stage([pair(too_large_utf8, "x")]))

    def test_accept_exact_utf8_budget_with_multibyte_source(self):
        exact = "é" * (LIMIT // 2)
        result = stage([pair(exact, "x")])
        self.assertIsNotNone(result)
        self.assertEqual(result[0][1], {})  # Overlong valid source, navigation omitted.

    def test_reject_three_byte_source_over_byte_limit(self):
        cjk = "中" * (LIMIT // 3 + 1)
        self.assertIsNone(stage([pair(cjk, "x")]))

    def test_reject_four_byte_source_over_byte_limit(self):
        emoji = "😀" * (LIMIT // 4 + 1)
        self.assertIsNone(stage([pair(emoji, "x")]))

    def test_reject_split_budget_violation_across_rows_and_hunks(self):
        large = "é" * (3 * 1024 * 1024)
        other = "é" * (2 * 1024 * 1024 + 1)
        value = [{"removed_sources": [(1, large)], "added_sources": []},
                 {"removed_sources": [(2, other)], "added_sources": []}]
        self.assertIsNone(stage(value))

    def test_accept_exact_ascii_utf8_budget(self):
        exact = "a" * LIMIT
        staged = stage([pair(exact, "x")])
        self.assertIsNotNone(staged)
        self.assertEqual(staged[0][1], {})

    def test_budget_independent_per_side(self):
        exact = "a" * LIMIT
        self.assertIsNotNone(stage([pair(exact, exact)]))

    def test_reject_ascii_one_byte_over_limit(self):
        self.assertIsNone(stage([pair("a" * (LIMIT + 1), "x")]))

    def test_reject_malformed_later_source_before_emitting_earlier_matches(self):
        data = [pair(), pair("Policy ⑩\nExtra", "Policy 10", number=10)]
        self.assertIsNone(stage(data))

    def test_invalid_source_never_prints_private_text(self):
        import contextlib
        import io
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream), contextlib.redirect_stderr(stream):
            self.assertIsNone(stage([pair("private-SSN-1234\nforged")]))
        self.assertEqual(stream.getvalue(), "")

    def test_source_records_are_unchanged(self):
        data = [pair("A ⑩\r\n", "A 10\r\n")]
        self.assertIsNotNone(stage(data))
        self.assertEqual(data, [pair("A ⑩\r\n", "A 10\r\n")])


if __name__ == "__main__":
    unittest.main()
