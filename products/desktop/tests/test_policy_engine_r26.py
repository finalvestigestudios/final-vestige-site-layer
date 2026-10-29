"""R26 engine entrypoint wiring; requires a complete repository checkout."""
import hashlib
import tempfile
import unittest
from pathlib import Path

from fvs_suite import engine


class PolicyEngineR26Tests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.before = self.root / "before.txt"
        self.after = self.root / "after.txt"

    def reports(self):
        return sorted(self.root.glob("policy-delta-*.txt"))

    def test_engine_writes_fingerprinted_human_review_report(self):
        original = b"Clause A\n"
        self.before.write_bytes(original)
        self.after.write_bytes(b"Clause B\n")
        report_path, = engine.policy_delta(self.before, self.after, self.root)
        report = report_path.read_text(encoding="utf-8")
        self.assertIn(hashlib.sha256(original).hexdigest(), report)
        self.assertIn("-Clause A", report)
        self.assertIn("+Clause B", report)
        self.assertIn("Not legal advice", report)

    def test_bad_second_input_cannot_create_partial_report(self):
        self.before.write_bytes(b"valid\n")
        self.after.write_bytes(b"invalid\x00hidden\n")
        with self.assertRaisesRegex(ValueError, "NUL"):
            engine.policy_delta(self.before, self.after, self.root)
        self.assertEqual(self.reports(), [])

    def test_unterminated_final_lines_do_not_concatenate(self):
        self.before.write_bytes(b"old")
        self.after.write_bytes(b"new")
        report_path, = engine.policy_delta(self.before, self.after, self.root)
        self.assertIn("-old\n\\ No newline at end of file\n+new",
                      report_path.read_text())

    def test_inputs_are_unchanged_on_success(self):
        old = b"\xef\xbb\xbfPolicy\n"
        new = b"Policy\n"
        self.before.write_bytes(old)
        self.after.write_bytes(new)
        engine.policy_delta(self.before, self.after, self.root)
        self.assertEqual(self.before.read_bytes(), old)
        self.assertEqual(self.after.read_bytes(), new)


if __name__ == "__main__":
    unittest.main()
