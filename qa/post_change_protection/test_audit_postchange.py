"""Adversarial synthetic fixtures for a strictly local evidence-only gate."""
import copy
import unittest

from audit_postchange import evaluate, instant


BASE = {
    'change': {'kind': 'plugin_activated', 'slug': 'fv-focus-popup', 'at': '2026-10-31T22:16:28Z'},
    'backup': {'started_at': '2026-11-01T02:42:35Z', 'completed_at': '2026-11-01T02:46:36Z',
               'last_attempt_failed': False, 'type': 'full',
               'plugins': ['fv-focus-popup', 'akismet'], 'errors': [], 'warnings': []},
    'scan': {'started_at': '2026-11-01T02:45:03+00:00', 'duration_seconds': 87,
             'progress': 100, 'error': False, 'threats': [], 'ignored_threats': []},
}


class AuditTests(unittest.TestCase):
    def run_change(self, section, key, value, expected):
        fixture = copy.deepcopy(BASE)
        fixture[section][key] = value
        out = evaluate(fixture)
        self.assertEqual(out['status'], 'HOLD')
        self.assertIn(expected, out['failures'])

    def test_current_evidence_passes(self):
        out = evaluate(copy.deepcopy(BASE))
        self.assertEqual(out['status'], 'PASS')
        self.assertEqual(out['failures'], [])

    def test_offset_time_comparison(self):
        self.assertEqual(instant('2026-11-01T02:45:03Z'), instant('2026-10-31T19:45:03-07:00'))

    def test_missing_time_zone_rejected(self):
        self.run_change('backup', 'started_at', '2026-11-01 02:42:35', 'INVALID_BACKUP_TIME')

    def test_bad_change_time(self):
        self.run_change('change', 'at', 'not-a-date', 'INVALID_CHANGE_TIME')

    def test_backup_precedes_activation(self):
        self.run_change('backup', 'started_at', '2026-10-31T20:00:00Z', 'BACKUP_PRE_DATES_CHANGE')

    def test_inconsistent_backup_order(self):
        self.run_change('backup', 'completed_at', '2026-11-01T02:00:00Z', 'BACKUP_TIME_ORDER')

    def test_latest_attempt_failed(self):
        self.run_change('backup', 'last_attempt_failed', True, 'BACKUP_LAST_ATTEMPT_UNVERIFIED')

    def test_last_attempt_unknown(self):
        self.run_change('backup', 'last_attempt_failed', None, 'BACKUP_LAST_ATTEMPT_UNVERIFIED')

    def test_partial_backup(self):
        self.run_change('backup', 'type', 'incremental', 'FULL_BACKUP_UNVERIFIED')

    def test_plugin_not_captured(self):
        self.run_change('backup', 'plugins', ['akismet'], 'PLUGIN_MISSING_FROM_BACKUP')

    def test_backup_warning(self):
        self.run_change('backup', 'warnings', ['unreadable-file'], 'BACKUP_ERRORS_OR_WARNINGS_UNVERIFIED')

    def test_backup_missing_warning_evidence(self):
        self.run_change('backup', 'warnings', None, 'BACKUP_ERRORS_OR_WARNINGS_UNVERIFIED')

    def test_scan_precedes_activation(self):
        self.run_change('scan', 'started_at', '2026-10-31T02:45:03Z', 'SCAN_PRE_DATES_CHANGE')

    def test_scan_error(self):
        self.run_change('scan', 'error', True, 'SCAN_INCOMPLETE_OR_FAILED')

    def test_scan_incomplete(self):
        self.run_change('scan', 'progress', 72, 'SCAN_INCOMPLETE_OR_FAILED')

    def test_active_scan_threat(self):
        self.run_change('scan', 'threats', [{'id': 1}], 'SCAN_THREATS_NOT_CLEARED')

    def test_ignored_scan_threat(self):
        self.run_change('scan', 'ignored_threats', [{'id': 1}], 'SCAN_THREATS_NOT_CLEARED')

    def test_bad_duration(self):
        self.run_change('scan', 'duration_seconds', -1, 'INVALID_SCAN_DURATION')

    def test_missing_kind(self):
        self.run_change('change', 'kind', None, 'UNSUPPORTED_CHANGE')

    def test_missing_plugin_slug(self):
        self.run_change('change', 'slug', '', 'MISSING_PLUGIN_IDENTITY')

    def test_empty_snapshot(self):
        self.assertEqual(evaluate({})['status'], 'HOLD')


if __name__ == '__main__':
    unittest.main()
