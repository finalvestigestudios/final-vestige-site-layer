"""Synthetic, offline regression cases; never touch a live service."""
import copy
import unittest
from post_change_coverage import inspect, utc


BASE = {
    'changes': [{'kind':'plugin', 'at':'2026-11-11T22:11:05Z', 'component':'review-only plugin'}],
    'scan': {'state':'idle', 'last_scan':{'started_at':'2026-11-11T04:32:09+00:00', 'error':False, 'progress':100}, 'threats':[]},
    'backup': {'backups':{'last_backup_when':'2026-11-11 04:31:53', 'last_attempt_when':'2026-11-11T04:32:09Z', 'last_attempt_status':'finished', 'last_attempt_failed':False}, 'restore_preflight_status':None},
    'restore': {'last_restore':{'has_restore_record':False}},
    'backup_log_warnings':[{'severity':'warn','message':'Connection encoding and table charset mismatch for table foo'}]
}
# Use timezone-aware dates in evidence payload. A naive provider date must be HOLD.
BASE['backup']['backups']['last_backup_when'] = '2026-11-11T04:31:53Z'


def status(sample, code):
    matches = [f for f in inspect(sample) if f['code'] == code]
    return matches[0]['status'] if matches else None


class PostChangeCoverageTests(unittest.TestCase):
    def test_utc_accepts_zulu(self):
        self.assertEqual(utc('2026-11-11T22:11:05Z').utcoffset().total_seconds(), 0)

    def test_utc_rejects_naive_time(self):
        self.assertIsNone(utc('2026-11-11 22:11:05'))

    def test_pre_activation_scan_is_hold(self):
        self.assertEqual(status(BASE, 'POST_CHANGE_SCAN'), 'HOLD')

    def test_pre_activation_backup_is_hold(self):
        self.assertEqual(status(BASE, 'POST_CHANGE_BACKUP'), 'HOLD')

    def test_latest_attempt_success_is_not_snapshot_freshness(self):
        x=copy.deepcopy(BASE)
        x['backup']['backups']['last_attempt_when'] = '2026-11-11T23:00:00Z'
        self.assertEqual(status(x, 'POST_CHANGE_BACKUP'), 'HOLD')

    def test_good_post_change_scan_covered_only(self):
        x=copy.deepcopy(BASE); x['scan']['last_scan']['started_at']='2026-11-11T23:00:00Z'
        self.assertEqual(status(x, 'POST_CHANGE_SCAN'), 'COVERED')

    def test_post_change_scan_with_error_is_hold(self):
        x=copy.deepcopy(BASE); x['scan']['last_scan'].update(started_at='2026-11-11T23:00:00Z',error=True)
        self.assertEqual(status(x,'POST_CHANGE_SCAN'), 'HOLD')

    def test_post_change_scan_in_progress_is_hold(self):
        x=copy.deepcopy(BASE); x['scan']['last_scan']['started_at']='2026-11-11T23:00:00Z'; x['scan']['state']='scanning'
        self.assertEqual(status(x,'POST_CHANGE_SCAN'), 'HOLD')

    def test_after_change_backup_covered_only(self):
        x=copy.deepcopy(BASE); x['backup']['backups']['last_backup_when']='2026-11-11T23:00:00Z'
        self.assertEqual(status(x,'POST_CHANGE_BACKUP'), 'COVERED')

    def test_backup_failed_after_snapshot_is_hold(self):
        x=copy.deepcopy(BASE); x['backup']['backups'].update(last_backup_when='2026-11-11T23:00:00Z',last_attempt_failed=True)
        self.assertEqual(status(x,'POST_CHANGE_BACKUP'), 'HOLD')

    def test_later_change_requires_new_check(self):
        x=copy.deepcopy(BASE); x['changes'].append({'at':'2026-11-12T00:05:00Z'})
        x['scan']['last_scan']['started_at']='2026-11-11T23:00:00Z'
        self.assertEqual(status(x,'POST_CHANGE_SCAN'), 'HOLD')

    def test_malformed_change_never_silently_passes(self):
        x=copy.deepcopy(BASE); x['changes'].append({'at':'yesterday'})
        self.assertEqual(status(x,'INVALID_CHANGE_TIME'), 'HOLD')
        self.assertIsNone(status(x,'POST_CHANGE_SCAN'))

    def test_missing_change_never_passes(self):
        x=copy.deepcopy(BASE); x['changes']=[]
        self.assertEqual(status(x,'NO_CHANGE_BASELINE'), 'HOLD')

    def test_charset_warning_is_review_not_proven_data_loss(self):
        self.assertEqual(status(BASE,'BACKUP_CHARSET_WARNING'), 'REVIEW')

    def test_unrelated_custom_plugin_warning_is_not_misclassified(self):
        x=copy.deepcopy(BASE); x['backup_log_warnings']=[{'message':'Version 0.2.1 not found in org API list'}]
        self.assertIsNone(status(x,'BACKUP_CHARSET_WARNING'))

    def test_no_restore_record_is_hold(self):
        self.assertEqual(status(BASE,'RESTORE_PROOF'), 'HOLD')

    def test_fake_restore_presence_not_marked_proven(self):
        x=copy.deepcopy(BASE); x['restore']['last_restore']['has_restore_record']=True; x['backup']['restore_preflight_status']='pass'
        self.assertEqual(status(x,'RESTORE_PROOF'), 'REVIEW')


if __name__=='__main__':
    unittest.main()
