"""Hermetic tests of fail-closed R105 browser acceptance journaling."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from qa_receipt_r105 import EvidenceJournal, FILENAME
from test_qa_artifacts_r107 import png, pdf


class ReceiptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.writer = EvidenceJournal(self.root)
        self.record = {'schema': 'fv.apollo.r104.real-wp-gallery.v1',
                       'release': 'STAGING_HOLD', 'real_wordpress_core_http': True,
                       'hosted_wordpress_or_assembler_verified': False,
                       'production_core_web_vitals': False,
                       'r103_interaction_cases': [
                           {'width': width, 'javascript_enabled': js,
                            'passed': True, 'actual_wordpress_http': True,
                            'reduced_motion': True, 'forced_colors': width == 320}
                           for width in (320, 390, 768, 1440, 1920)
                           for js in (False, True)],
                       'axe': [{'width': width, 'state': 'selected_two_sources',
                                'passes': 12, 'violations': []} for width in (390, 1440)],
                       'performance_lab_samples': [
                           {'width': width, 'trial': t, 'lcp_ms': 250, 'cls': 0.01}
                           for width in (390, 1440) for t in range(1, 4)],
                       'screenshots_sha256': {}, 'pdf_sha256': {}}
        for name in ('R104_REAL_WP_SELECTED_320.png', 'R104_REAL_WP_SELECTED_390.png',
                     'R104_REAL_WP_SELECTED_1440.png', 'R104_REAL_WP_NOJS_390.png'):
            (self.root / name).write_bytes(png(int(name.rsplit('_', 1)[-1][:-4])))
            self.record['screenshots_sha256'][name] = hashlib.sha256((self.root / name).read_bytes()).hexdigest()
        name = 'R104_REAL_WP_PRINT.pdf'
        (self.root / name).write_bytes(pdf())
        self.record['pdf_sha256'][name] = hashlib.sha256((self.root / name).read_bytes()).hexdigest()

    def test_checkpoint_never_claims_complete(self):
        self.writer.checkpoint(self.record, 'interaction:320:js')
        data = json.loads((self.root / FILENAME).read_text())
        self.assertEqual(data['status'], 'in_progress')
        self.assertFalse(data['complete'])
        self.assertEqual(data['counts']['browser_cases'], 10)

    def test_success_only_with_full_evidence(self):
        self.writer.complete(self.record)
        data = json.loads((self.root / FILENAME).read_text())
        self.assertEqual(data['status'], 'completed')
        self.assertTrue(data['complete'])
        self.assertEqual(len(data['artifact_sha256']), 5)

    def test_browser_failure_rejected(self):
        self.record['r103_interaction_cases'][3]['passed'] = False
        with self.assertRaisesRegex(ValueError, 'INCOMPLETE_BROWSER'):
            self.writer.complete(self.record)

    def test_selected_state_axe_failure_rejected(self):
        self.record['axe'][1]['violations'] = [{'id': 'color-contrast'}]
        with self.assertRaisesRegex(ValueError, 'INCOMPLETE_AXE'):
            self.writer.complete(self.record)

    def test_performance_budget_not_relaxed(self):
        self.record['performance_lab_samples'][0]['lcp_ms'] = 2501
        with self.assertRaisesRegex(ValueError, 'FAILED_LCP'):
            self.writer.complete(self.record)

    def test_missing_observation_rejected(self):
        for s in self.record['performance_lab_samples']:
            if s['width'] == 390:
                s['lcp_ms'] = None
        with self.assertRaisesRegex(ValueError, 'MISSING_OR_FAILED_LCP'):
            self.writer.complete(self.record)

    def test_corrupt_screenshot_rejected(self):
        (self.root / 'R104_REAL_WP_SELECTED_390.png').write_bytes(b'\x89PNG\r\n\x1a\n' + b'altered')
        with self.assertRaisesRegex(ValueError, 'HASH_MISMATCH'):
            self.writer.complete(self.record)

    def test_failed_receipt_never_leaks_exception(self):
        self.writer.checkpoint(self.record, 'browser:390:js')
        self.writer.fail('TimeoutError; password=do-not-log')
        data = json.loads((self.root / FILENAME).read_text())
        self.assertEqual(data['exception_type'], 'UnknownError')
        self.assertEqual(data['last_checkpoint'], 'browser:390:js')
        self.assertFalse(data['complete'])
        self.assertNotIn('do-not-log', json.dumps(data))

    def test_invalid_stage_rejected(self):
        with self.assertRaisesRegex(ValueError, 'INVALID_STAGE'):
            self.writer.checkpoint(self.record, 'https://site/?token=secret')

    def test_completed_cannot_be_overwritten_failed(self):
        self.writer.complete(self.record)
        with self.assertRaisesRegex(ValueError, 'IMMUTABLE'):
            self.writer.fail('AssertionError')

    def test_crash_is_atomic_no_tmp(self):
        self.writer.checkpoint(self.record, 'start')
        self.assertFalse((self.root / 'R105_QA_PROGRESS.json.tmp').exists())


    def test_duplicate_browser_case_rejected(self):
        self.record['r103_interaction_cases'][1] = dict(self.record['r103_interaction_cases'][0])
        with self.assertRaisesRegex(ValueError, 'INCOMPLETE_BROWSER_MATRIX'):
            self.writer.complete(self.record)

    def test_forged_browser_case_rejected(self):
        self.record['r103_interaction_cases'][0]['actual_wordpress_http'] = False
        with self.assertRaisesRegex(ValueError, 'INCOMPLETE_BROWSER_MATRIX'):
            self.writer.complete(self.record)

    def test_boolean_success_rejected(self):
        self.record['r103_interaction_cases'][0]['passed'] = 1
        with self.assertRaisesRegex(ValueError, 'INCOMPLETE_BROWSER_MATRIX'):
            self.writer.complete(self.record)

    def test_wrong_axe_state_rejected(self):
        self.record['axe'][0]['state'] = 'unselected'
        with self.assertRaisesRegex(ValueError, 'INCOMPLETE_AXE'):
            self.writer.complete(self.record)

    def test_missing_axe_passes_rejected(self):
        del self.record['axe'][0]['passes']
        with self.assertRaisesRegex(ValueError, 'INCOMPLETE_AXE'):
            self.writer.complete(self.record)

    def test_nan_cls_rejected(self):
        self.record['performance_lab_samples'][0]['cls'] = float('nan')
        with self.assertRaisesRegex(ValueError, 'INVALID_OR_FAILED_CLS'):
            self.writer.complete(self.record)

    def test_infinite_lcp_rejected(self):
        self.record['performance_lab_samples'][0]['lcp_ms'] = float('inf')
        with self.assertRaisesRegex(ValueError, 'MISSING_OR_FAILED_LCP'):
            self.writer.complete(self.record)

    def test_missing_one_lcp_rejected(self):
        self.record['performance_lab_samples'][0]['lcp_ms'] = None
        with self.assertRaisesRegex(ValueError, 'MISSING_OR_FAILED_LCP'):
            self.writer.complete(self.record)

    def test_boolean_cls_rejected(self):
        self.record['performance_lab_samples'][0]['cls'] = False
        with self.assertRaisesRegex(ValueError, 'INVALID_OR_FAILED_CLS'):
            self.writer.complete(self.record)

    def test_duplicate_trial_rejected(self):
        self.record['performance_lab_samples'][1]['trial'] = 1
        with self.assertRaisesRegex(ValueError, 'MISSING_LAB_TRIAL'):
            self.writer.complete(self.record)

    def test_wrong_scope_rejected(self):
        self.record['hosted_wordpress_or_assembler_verified'] = True
        with self.assertRaisesRegex(ValueError, 'SCOPE_MISMATCH'):
            self.writer.complete(self.record)

    def test_relabelled_artifact_rejected(self):
        name = 'R104_REAL_WP_SELECTED_390.png'
        self.record['screenshots_sha256']['R104_REAL_WP_HIDDEN_390.png'] = self.record['screenshots_sha256'].pop(name)
        with self.assertRaisesRegex(ValueError, 'INCOMPLETE_ARTIFACT_SET'):
            self.writer.complete(self.record)

    def test_wrong_magic_bytes_rejected(self):
        name = 'R104_REAL_WP_SELECTED_390.png'
        (self.root / name).write_bytes(b'pretend-png')
        self.record['screenshots_sha256'][name] = hashlib.sha256(b'pretend-png').hexdigest()
        with self.assertRaisesRegex(ValueError, 'INVALID_PNG_BYTES'):
            self.writer.complete(self.record)

    def test_completed_checkpoint_immutable(self):
        self.writer.complete(self.record)
        with self.assertRaisesRegex(ValueError, 'IMMUTABLE'):
            self.writer.checkpoint(self.record, 'restart')
        self.assertTrue(json.loads((self.root / FILENAME).read_text())['complete'])

    def test_non_string_stage_rejected(self):
        with self.assertRaisesRegex(ValueError, 'INVALID_STAGE'):
            self.writer.checkpoint(self.record, 5)

    def test_repeated_completion_immutable(self):
        self.writer.complete(self.record)
        with self.assertRaisesRegex(ValueError, 'IMMUTABLE'):
            self.writer.complete(self.record)

if __name__ == '__main__':
    unittest.main()
