"""Synthetic offline tests for the security-fix/recovery chronology gate."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from recovery_gate import check, utc, version_tuple

FIXTURE = {
    'fixed_version': '3.7.5',
    'plugin': {'version': '3.7.5', 'status': 'active'},
    'scan': {
        'state': 'idle', 'threats': [], 'ignored_threats': [],
        'recent_fixes': [{'status': 'fixed', 'description': 'burst-statistics known issue',
                          'fixed_on': '2026-11-14T02:30:35Z'}],
        'last_scan': {'started_at': '2026-11-14T02:27:21+00:00', 'error': False, 'progress': 100}
    },
    'backup': {'backups': {'last_attempt_failed': False, 'last_attempt_status': 'finished'}},
    'activity': [{'action': 'backup_complete_full', 'date': '2026-11-14T02:29:17Z'}]
}


class RecoveryGateTest(unittest.TestCase):
    def results(self, fixture=None):
        return {g['gate']: g['status'] for g in check(FIXTURE if fixture is None else fixture)}

    def test_current_snapshot_holds_pre_fix_backup_and_scan(self):
        x = self.results()
        self.assertEqual(x['PATCHED_PLUGIN_ACTIVE'], 'PASS')
        self.assertEqual(x['POST_FIX_FULL_BACKUP'], 'HOLD')
        self.assertEqual(x['POST_FIX_CLEAN_SCAN'], 'HOLD')

    def test_post_fix_full_backup_and_scan_pass_when_evidenced(self):
        s = copy.deepcopy(FIXTURE)
        s['activity'][0]['date'] = '2026-11-14T03:00:00Z'
        s['scan']['last_scan']['started_at'] = '2026-11-14T03:00:01Z'
        self.assertTrue(all(x == 'PASS' for x in self.results(s).values()))

    def test_old_plugin_holds(self):
        s = copy.deepcopy(FIXTURE); s['plugin']['version'] = '3.7.4'
        self.assertEqual(self.results(s)['PATCHED_PLUGIN_ACTIVE'], 'HOLD')

    def test_inactive_plugin_not_counted_as_active_patch(self):
        s = copy.deepcopy(FIXTURE); s['plugin']['status'] = 'inactive'
        self.assertEqual(self.results(s)['PATCHED_PLUGIN_ACTIVE'], 'HOLD')

    def test_ignored_threat_holds(self):
        s = copy.deepcopy(FIXTURE); s['scan']['ignored_threats'] = [{'id': 5}]
        self.assertEqual(self.results(s)['NO_REPORTED_ACTIVE_THREAT'], 'HOLD')

    def test_missing_scan_must_fail_closed(self):
        s = copy.deepcopy(FIXTURE); s['scan'].pop('last_scan')
        self.assertEqual(self.results(s)['POST_FIX_CLEAN_SCAN'], 'HOLD')

    def test_same_time_not_post_fix(self):
        s = copy.deepcopy(FIXTURE); s['activity'][0]['date'] = '2026-11-14T02:30:35Z'
        self.assertEqual(self.results(s)['POST_FIX_FULL_BACKUP'], 'HOLD')

    def test_missing_fix_time_fails_closed(self):
        s = copy.deepcopy(FIXTURE); s['scan']['recent_fixes'] = []
        self.assertEqual(self.results(s)['FIX_EVENT_TIMESTAMPED'], 'HOLD')

    def test_backup_attempt_failure_blocks(self):
        s = copy.deepcopy(FIXTURE)
        s['activity'][0]['date'] = '2026-11-14T03:01:00Z'
        s['backup']['backups']['last_attempt_failed'] = True
        self.assertEqual(self.results(s)['POST_FIX_FULL_BACKUP'], 'HOLD')

    def test_incomplete_scan_progress_fails_closed(self):
        for progress in (0, 20, 99, None, '100', True):
            with self.subTest(progress=progress):
                s = copy.deepcopy(FIXTURE)
                s['scan']['last_scan']['started_at'] = '2026-11-14T03:01:00Z'
                s['scan']['last_scan']['progress'] = progress
                self.assertEqual(self.results(s)['POST_FIX_CLEAN_SCAN'], 'HOLD')

    def test_missing_scan_progress_fails_closed(self):
        s = copy.deepcopy(FIXTURE)
        s['scan']['last_scan']['started_at'] = '2026-11-14T03:01:00Z'
        del s['scan']['last_scan']['progress']
        self.assertEqual(self.results(s)['POST_FIX_CLEAN_SCAN'], 'HOLD')

    def test_scan_still_in_progress_fails_closed(self):
        s = copy.deepcopy(FIXTURE)
        s['scan']['last_scan']['started_at'] = '2026-11-14T03:01:00Z'
        s['scan']['state'] = 'scanning'
        self.assertEqual(self.results(s)['POST_FIX_CLEAN_SCAN'], 'HOLD')

    def test_scan_error_blocks(self):
        s = copy.deepcopy(FIXTURE)
        s['scan']['last_scan'] = {'started_at': '2026-11-14T03:01:00Z','error':True}
        self.assertEqual(self.results(s)['POST_FIX_CLEAN_SCAN'], 'HOLD')

    def test_unqualified_time_rejected(self):
        self.assertIsNone(utc('2026-11-14T03:00:00'))
        self.assertIsNone(utc('garbage'))

    def test_untrusted_version_rejected(self):
        self.assertIsNone(version_tuple('3.7.5;rm -rf'))
        self.assertIsNone(version_tuple('preview'))

    def test_cli_holds_for_current_snapshot(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'snapshot.json'; f.write_text(json.dumps(FIXTURE),encoding='utf-8')
            r=subprocess.run([sys.executable,str(Path(__file__).with_name('recovery_gate.py')),str(f)],capture_output=True,text=True)
            self.assertEqual(r.returncode,1)
            self.assertIn('HOLD POST_FIX_FULL_BACKUP',r.stdout)

    def test_cli_passes_only_complete_post_fix_evidence(self):
        s=copy.deepcopy(FIXTURE)
        s['activity'][0]['date']='2026-11-14T03:00:00Z'
        s['scan']['last_scan']['started_at']='2026-11-14T03:00:01Z'
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'snapshot.json'; f.write_text(json.dumps(s),encoding='utf-8')
            r=subprocess.run([sys.executable,str(Path(__file__).with_name('recovery_gate.py')),str(f)],capture_output=True,text=True)
            self.assertEqual(r.returncode,0)

if __name__ == '__main__':
    unittest.main()
