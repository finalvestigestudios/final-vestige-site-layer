"""R447: portable Windows x64 basename custody for premium evidence labels.

All cases use synthetic names, never customer data or network access.
"""
from __future__ import annotations

import json
import unittest

from fvs_suite.evidence_label import canonical_evidence_label


class WindowsEvidenceBasenameR447(unittest.TestCase):
    def test_visible_international_names_keep_exact_json_roundtrip(self):
        for name in ("grant 2026.csv", "Résumé 東京.csv", "Ångström-∆.csv",
                     "Com10.csv", "CONsolidated.csv", "LPT10.xlsx",
                     "budget.v2.csv", "販売費🧾.csv", "normal name.csv"):
            with self.subTest(name=name):
                encoded = canonical_evidence_label(name)
                self.assertEqual(json.loads('"' + encoded + '"'), name)
                self.assertEqual(encoded, json.dumps(name, ensure_ascii=True)[1:-1])

    def test_win32_forbidden_characters_and_ads_colons_fail_closed(self):
        for name in ('ledger:2026.csv', 'src<1.csv', 'src>1.csv',
                     'src"1.csv', 'src|1.csv', 'src?1.csv',
                     'src*1.csv', r'src\1.csv', 'src/1.csv'):
            with self.subTest(name=name):
                with self.assertRaisesRegex(ValueError, "Invalid evidence filename label"):
                    canonical_evidence_label(name)

    def test_device_aliases_and_leading_trailing_shell_names_fail_closed(self):
        for name in ("report.", "report ", " ledger.csv", ". ",
                     "CON", "con.txt", "Con .CSV", "prn.csv", "AUX.XLS",
                     "nul", "NUL..CSV", "COM1.csv", "COM9",
                     "com¹.csv", "COM².doc", "COM³.txt",
                     "LPT1.csv", "LPT9.txt", "lpt¹", "LPT².csv",
                     "LPT³.csv", "CONIN$.txt", "CONOUT$.txt"):
            with self.subTest(name=name):
                with self.assertRaisesRegex(ValueError, "Invalid evidence filename label"):
                    canonical_evidence_label(name)

    def test_utf16_component_limits_and_invisible_unicode(self):
        self.assertEqual(canonical_evidence_label("a" * 255), "a" * 255)
        for name in ("a" * 256, "🧾" * 128, "\u202einput.csv",
                     "x\u00a0.csv", "x\ud800.csv"):
            with self.subTest(length=len(name)):
                with self.assertRaises(ValueError):
                    canonical_evidence_label(name)

    def test_custom_str_subclass_not_executed(self):
        class MaliciousName(str):
            def __str__(self):
                raise RuntimeError("PRIVATE CUSTOMER NAME")

            def __hash__(self):
                raise RuntimeError("PRIVATE CUSTOMER NAME")

        with self.assertRaisesRegex(ValueError, "Invalid evidence filename label"):
            canonical_evidence_label(MaliciousName("invoice.csv"))


if __name__ == "__main__":
    unittest.main()
