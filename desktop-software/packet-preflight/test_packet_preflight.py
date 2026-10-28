import json
import tempfile
import unittest
from pathlib import Path
from packet_preflight import preflight, render_html, validate_rules, STARTER_RULES


class PacketPreflightTests(unittest.TestCase):
    def test_requirement_errors_and_unmatched_files(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            packet = root / "packet"
            packet.mkdir()
            (packet / "application.pdf").write_bytes(b"")
            (packet / "application2.pdf").write_bytes(b"A" * 1024)
            (packet / "extra.txt").write_text("extra", encoding="utf-8")
            rules = root / "rules.json"
            rules.write_text(json.dumps({"title": "Test packet", "rules": [
                {"name": "Application", "pattern": "application*.pdf", "minimum": 1, "maximum": 1, "allow_empty": False},
                {"name": "Invoice", "pattern": "invoice*.pdf", "minimum": 1, "maximum": 1},
            ]}), encoding="utf-8")
            result = preflight(packet, rules)
            self.assertEqual(result["status"], "CHECK")
            self.assertIn("TOO_MANY", result["issue_counts"])
            self.assertIn("TOO_FEW", result["issue_counts"])
            self.assertIn("EMPTY", result["issue_counts"])
            self.assertEqual(result["unmatched_files"], ["extra.txt"])
            self.assertIn("<table>", render_html(result))

    def test_matching_relative_glob(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            packet = root / "packet"
            packet.mkdir()
            (packet / "application.pdf").write_bytes(b"ok")
            rules = root / "rules.json"
            rules.write_text(json.dumps({"rules": [
                {"name": "PDF", "pattern": "**/*.pdf", "minimum": 1, "maximum": 1}
            ]}), encoding="utf-8")
            self.assertEqual(preflight(packet, rules)["status"], "PASS")

    def test_disallow_unsafe_patterns_and_invalid_limits(self):
        for pattern in ("../data/*", "/etc/*", "C:/Temp/*", r"..\anything"):
            with self.assertRaises(ValueError):
                validate_rules({"rules": [{"name": "Bad", "pattern": pattern}]})
        with self.assertRaises(ValueError):
            validate_rules({"rules": [{"name": "Bad", "pattern": "*.pdf", "minimum": 3, "maximum": 1}]})

    def test_html_escapes_rule_labels(self):
        report = {"results":[{"name":"<script>", "pattern":"*", "matched":0,"status":"CHECK",
                              "problems":[{"code":"TOO_FEW","detail":"none"}]}],
                  "unmatched_files":[], "scan_errors":[], "status":"CHECK",
                  "checklist":"Example", "issues_total":1}
        html = render_html(report)
        self.assertNotIn("<script>", html)
        self.assertIn("&lt;script&gt;", html)

    def test_starter_rules_are_valid(self):
        validate_rules(STARTER_RULES)


if __name__ == "__main__":
    unittest.main()
