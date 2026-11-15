"""Fully synthetic, offline tests. Never use private WordPress data."""
import unittest
from backup_warning_audit import audit


def entry(message, job=1, severity="warn", feature="vaultpress-backup"):
    return {"client_id": job, "severity": severity, "feature": feature, "message": message}


WARN = "warn: Connection encoding and table charset mismatch for table `example_only`. Table charset: `utf8mb4`, Connection charset: `latin1`."


class BackupWarningTests(unittest.TestCase):
    def test_two_jobs_not_double_counted(self):
        r = audit({"logs": [entry(WARN, 10), entry(WARN, 10), entry(WARN, 11)]})
        self.assertEqual((r["status"], r["warning_events"], r["distinct_jobs_with_warning"]),
                         ("RESTORE_FIDELITY_REVIEW", 3, 2))

    def test_unicode_restoration_not_falsely_certified(self):
        self.assertIn("not proof", audit({"logs": [entry(WARN)]})["meaning"])

    def test_empty_log_never_says_restored(self):
        self.assertEqual(audit({"logs": []})["status"], "NO_MATCH_IN_SUPPLIED_LOGS")

    def test_missing_logs_unknown(self):
        self.assertEqual(audit({})["status"], "UNKNOWN")

    def test_malformed_events_ignored(self):
        self.assertEqual(audit({"logs": [None, "bad", 9, {}]})["warning_events"], 0)

    def test_non_backup_warning_ignored(self):
        self.assertEqual(audit({"logs": [entry(WARN, feature="other")]})["warning_events"], 0)

    def test_unrelated_plugin_warning_ignored(self):
        self.assertEqual(audit({"logs": [entry("Plugin version not found in registry")]})["warning_events"], 0)

    def test_only_warning_or_error_counted(self):
        self.assertEqual(audit({"logs": [entry(WARN, severity="info")]})["warning_events"], 0)

    def test_same_charset_not_flagged(self):
        same = WARN.replace("latin1", "utf8mb4")
        self.assertEqual(audit({"logs": [entry(same)]})["warning_events"], 0)

    def test_raw_table_name_never_returned(self):
        self.assertNotIn("example_only", str(audit({"logs": [entry(WARN)]})))


if __name__ == "__main__":
    unittest.main()
