"""Hermetic tests of fail-closed R105 browser acceptance journaling."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from qa_receipt_r105 import EvidenceJournal, FILENAME


class ReceiptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.writer = EvidenceJournal(self.root)
        self.record = {'r103_interaction_cases': [{'passed': True} for _ in range(10)],
                       'axe': [{'violations': []} for _ in range(2)],
                       'performance_lab_samples': [
                           {'width': width, 'trial': t, 'lcp_ms': 250, 'cls': 0.01}
                           for width in (390, 1440) for t in range(1, 4)],
                       'screenshots_sha256': {}, 'pdf_sha256': {}}
        for name in ('R104_REAL_WP_SELECTED_320.png', 'R104_REAL_WP_SELECTED_390.png',
                     'R104_REAL_WP_SELECTED_1440.png', 'R104_REAL_WP_NOJS_390.png'):
            (self.root / name).write_bytes(name.encode())
            self.record['screenshots_sha256'][name] = hashlib.sha256(name.encode()).hexdigest()
        name = 'R104_REAL_WP_PRINT.pdf'
        (self.root / name).write_bytes(name.encode())
        self.record['pdf_sha256'][name] = hashlib.sha256(name.encode()).hexdigest()

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
        (self.root / 'R104_REAL_WP_SELECTED_390.png').write_bytes(b'altered')
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


if __name__ == '__main__':
    unittest.main()
