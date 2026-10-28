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


    def test_root_glob_does_not_match_nested_file(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            packet = root / "packet"
            (packet / "archive").mkdir(parents=True)
            (packet / "archive" / "application.pdf").write_bytes(b"pdf")
            rules = root / "rules.json"
            rules.write_text(json.dumps({"rules": [
                {"name": "Required root application", "pattern": "application*.pdf", "minimum": 1}
            ]}), encoding="utf-8")
            result = preflight(packet, rules)
            self.assertEqual(result["status"], "CHECK")
            self.assertEqual(result["issue_counts"]["TOO_FEW"], 1)
            self.assertEqual(result["unmatched_files"], ["archive/application.pdf"])

    def test_extra_files_overlap_and_total_size_are_explicit(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            packet = root / "packet"
            packet.mkdir()
            (packet / "invoice.pdf").write_bytes(b"x" * 1024)
            (packet / "extra.txt").write_bytes(b"extra")
            rules = root / "rules.json"
            rules.write_text(json.dumps({
                "forbid_unmatched": True, "max_total_size_mb": 0.0001,
                "rules": [
                    {"name": "Root PDFs", "pattern": "*.pdf"},
                    {"name": "Any PDF", "pattern": "**/*.pdf"}
                ]
            }), encoding="utf-8")
            result = preflight(packet, rules)
            self.assertEqual(result["status"], "CHECK")
            self.assertEqual(result["issue_counts"]["OVERLAPPING_RULES"], 1)
            self.assertEqual(result["issue_counts"]["UNMATCHED_FILE"], 1)
            self.assertEqual(result["issue_counts"]["TOTAL_OVERSIZE"], 1)
            self.assertEqual(result["overlapping_files"][0]["file"], "invoice.pdf")
            self.assertIn("Overlapping rule matches", render_html(result))

    def test_snapshot_changes_when_files_change(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            packet = root / "packet"
            packet.mkdir()
            path = packet / "application.pdf"
            path.write_bytes(b"one")
            rules = root / "rules.json"
            rules.write_text(json.dumps({"rules": [{"name": "Application", "pattern": "*.pdf"}]}),
                             encoding="utf-8")
            first = preflight(packet, rules)
            path.write_bytes(b"two-three")
            second = preflight(packet, rules)
            self.assertNotEqual(first["source_snapshot_sha256"], second["source_snapshot_sha256"])
            self.assertEqual(first["rules_sha256"], second["rules_sha256"])

    def test_export_clobber_blocked_through_command_line(self):
        import sys
        from unittest.mock import patch
        from packet_preflight import main
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            packet = root / "packet"
            packet.mkdir()
            (packet / "application.pdf").write_bytes(b"valid")
            rules = root / "rules.json"
            rules.write_text(json.dumps({"rules": [{"name": "Application", "pattern": "*.pdf"}]}),
                             encoding="utf-8")
            report = root / "report.json"
            report.write_text("PROTECT THIS REPORT", encoding="utf-8")
            with patch.object(sys, "argv", ["packet-preflight", str(packet), "--rules", str(rules),
                                            "--report", str(report)]):
                self.assertEqual(main(), 2)
            self.assertEqual(report.read_text(encoding="utf-8"), "PROTECT THIS REPORT")
            with patch.object(sys, "argv", ["packet-preflight", str(packet), "--rules", str(rules),
                                            "--report", str(packet / "report.html")]):
                self.assertEqual(main(), 2)
            self.assertFalse((packet / "report.html").exists())

    def test_skipped_directory_symlink_disqualifies_clean_result(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            packet = root / "packet"
            packet.mkdir()
            (packet / "application.pdf").write_bytes(b"valid")
            outside = root / "linked"
            outside.mkdir()
            try:
                (packet / "shortcut").symlink_to(outside, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("Creating directory symlinks requires elevated permissions on this machine")
            rules = root / "rules.json"
            rules.write_text(json.dumps({"rules": [{"name": "Application", "pattern": "*.pdf"}]}),
                             encoding="utf-8")
            result = preflight(packet, rules)
            self.assertEqual(result["status"], "CHECK")
            self.assertEqual(result["issue_counts"]["SCAN_ERROR"], 1)



if __name__ == "__main__":
    unittest.main()
