import unittest
from ical_utils import fold_ical_line, render_ical_lines


class IcalFoldingTests(unittest.TestCase):
    def test_ascii_and_utf8_remain_under_75_octets(self):
        for original in ("SUMMARY:" + "a" * 280,
                         "DESCRIPTION:" + ("Résumé ☃ 🗓️ — " * 70),
                         "X-EMPTY:", "SUMMARY:short"):
            folded = fold_ical_line(original)
            self.assertTrue(all(len(line.encode("utf-8")) <= 75 for line in folded))
            self.assertEqual(folded[0] + "".join(line[1:] for line in folded[1:]), original)
            self.assertTrue(all(line.startswith(" ") for line in folded[1:]))

    def test_unescaped_newlines_and_non_text_are_rejected(self):
        for bad in ("X:hello\nY:other", "X:hello\rY:other", 24):
            with self.assertRaises(ValueError):
                fold_ical_line(bad)

    def test_serializer_uses_crlf_and_folds_unicode(self):
        result = render_ical_lines(["BEGIN:VCALENDAR", "SUMMARY:" + "É" * 100, "END:VCALENDAR"])
        self.assertTrue(result.endswith("\r\n"))
        self.assertNotIn("\n", result.replace("\r\n", ""))
        self.assertTrue(all(len(line.encode("utf-8")) <= 75 for line in result.split("\r\n") if line))


if __name__ == "__main__":
    unittest.main()
