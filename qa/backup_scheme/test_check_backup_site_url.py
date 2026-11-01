"""No network, CMS, filesystem writes or production dependency: synthetic fixtures only."""

import copy
import io
import json
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from check_backup_site_url import check, main


def fixture(home="https://example.test", backup_urls=("http://example.test",)):
    return {
        "settings": {"general": {"home": home, "siteurl": home}},
        "activity": {"activities": [
            {"date": "2026-11-01T02:46:36Z", "object": {"backup_info": {
                "backup_stats": json.dumps({"site_url": url, "plugins": {"count": 21}})}}}
            for url in backup_urls]},
    }


class Checks(unittest.TestCase):
    def test_real_observation_shape_is_review_not_outage_claim(self):
        s = fixture(backup_urls=("http://example.test",) * 7)
        x = check(s)
        self.assertEqual(x["classification"], "REVIEW")
        self.assertEqual(x["examined_backups"], 7)
        self.assertEqual(x["scheme_mismatches"], 7)
        self.assertIn("not a restore", x["interpretation"])

    def test_identical_https_matches(self):
        self.assertEqual(check(fixture(backup_urls=("https://example.test",)))["classification"], "MATCH")

    def test_http_canonical_and_http_backup_matches(self):
        self.assertEqual(check(fixture("http://example.test"))["classification"], "MATCH")

    def test_host_mismatch(self):
        x = check(fixture(backup_urls=("https://other.test",)))
        self.assertEqual(x["host_or_port_mismatches"], 1)
        self.assertEqual(x["classification"], "REVIEW")

    def test_explicit_port_mismatch(self):
        self.assertEqual(check(fixture(backup_urls=("https://example.test:8443",)))["classification"], "REVIEW")

    def test_no_backup_entries(self):
        self.assertEqual(check(fixture(backup_urls=()))["classification"], "INSUFFICIENT_DATA")

    def test_mixed_backup_schemes(self):
        x = check(fixture(backup_urls=("https://example.test", "http://example.test")))
        self.assertEqual((x["examined_backups"], x["scheme_mismatches"]), (2, 1))

    def test_unparseable_backup_does_not_crash(self):
        x = fixture()
        x["activity"]["activities"][0]["object"]["backup_info"]["backup_stats"] = "{bad json"
        self.assertEqual(check(x)["classification"], "INSUFFICIENT_DATA")
        self.assertEqual(check(x)["malformed"], 1)

    def test_invalid_current_site_url_rejected(self):
        for value in ("javascript:alert(1)", "https://a.test/?secret=1", "https://user:pass@a.test/"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    check(fixture(home=value))

    def test_inconsistent_canonical_settings_flagged(self):
        x = fixture()
        x["settings"]["general"]["siteurl"] = "http://example.test"
        self.assertEqual(check(x)["reason"], "CANONICAL_SETTINGS_DISAGREE")

    def test_no_personal_data_echoed(self):
        x = fixture()
        x["subscriber_email"] = "private@secret.test"
        self.assertNotIn("private@secret.test", json.dumps(check(x)))

    def test_cli_stdin(self):
        raw = json.dumps(fixture())
        output = io.StringIO()
        with patch("sys.stdin", io.StringIO(raw)), redirect_stdout(output):
            code = main(["-"])
        self.assertEqual(code, 0)
        self.assertIn('"classification": "REVIEW"', output.getvalue())

    def test_cli_invalid_json(self):
        out = io.StringIO()
        with patch("sys.stdin", io.StringIO("not-json")), redirect_stdout(out):
            code = main(["-"])
        self.assertEqual(code, 2)
        self.assertIn("INVALID_INPUT", out.getvalue())


if __name__ == "__main__":
    unittest.main()
