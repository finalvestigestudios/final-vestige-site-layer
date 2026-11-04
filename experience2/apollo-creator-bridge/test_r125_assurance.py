#!/usr/bin/env python3
"""R125 fail-closed receipt regressions. Synthetic receipts NEVER count as actual browser QA."""
import copy
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from qa_r125_assurance import assess, blob_id, digest

ROOT = Path(__file__).resolve().parent

class AssuranceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.files = self.base / 'evidence'
        self.files.mkdir()
        self.src = self.base / 'src'
        self.src.mkdir()
        for name in ('landing-preview.html', 'qa_r113_print.py'):
            shutil.copyfile(ROOT / name, self.src / name)
        for name, contents in (
            ('R113_WEB_390.png', b'\x89PNG\r\n\x1a\n390-synthetic'),
            ('R113_WEB_1440.png', b'\x89PNG\r\n\x1a\n1440-synthetic'),
            ('R113_CLASSROOM_PRINT_390.pdf', b'%PDF-1.7 synthetic entire packet'),
            ('R120_STUDENT_ONLY_PRINT_390.pdf', b'%PDF-1.7 synthetic student packet'),
        ):
            (self.files / name).write_bytes(contents)
        self.blob = blob_id((self.src / 'landing-preview.html').read_bytes())
        self.receipt = self.files / 'R113_BROWSER_RECEIPT.json'
        self.data = {
            'source_identity': 'EXACT_GIT_HEAD', 'classification': 'actual-source',
            'source_sha256': digest(self.src / 'landing-preview.html'), 'browser': '144.0.7559.96',
            'modes': [f'{w}px-js-{int(js)}' for w in (320,360,390,768,1024,1440,1920) for js in (False,True)],
            'performance': [{'width':w,'trial':t,'lcp_ms':110.0,'cls':0.0,'lab_only':True}
                            for w in (390,1440) for t in (1,2,3)],
            'screenshots': {name:digest(self.files / name) for name in ('R113_WEB_390.png','R113_WEB_1440.png')},
            'pdf': {'name':'R113_CLASSROOM_PRINT_390.pdf','sha256':digest(self.files / 'R113_CLASSROOM_PRINT_390.pdf')},
            'worksheet_pdf': {'name':'R120_STUDENT_ONLY_PRINT_390.pdf','sha256':digest(self.files / 'R120_STUDENT_ONLY_PRINT_390.pdf')},
            'axe_scans': [{'width':w,'state':st,'violations':0,'ids':[], 'incomplete':0,'passes':60}
                          for w in (390,1440) for st in ('all','limit')],
        }
        self.receipt.write_text(json.dumps(self.data), encoding='utf-8')

    def audit(self, change=None, blob=None):
        state = copy.deepcopy(self.data)
        if change: change(state)
        self.receipt.write_text(json.dumps(state), encoding='utf-8')
        return assess(self.receipt, blob or self.blob, self.src)

    def test_nominal_synthetic_contract_only(self):
        result = self.audit()
        self.assertEqual(result['classification'], 'BROWSER_QA_CHECKED_NOT_RELEASE_APPROVED')
        self.assertEqual(result['release_gate'], 'STAGING_HOLD')
        self.assertTrue(all(result['checks'].values()))

    def test_git_blob_calculation(self):
        self.assertEqual(blob_id((self.src / 'landing-preview.html').read_bytes()), self.blob)

    def test_wrong_blob_fails(self):
        self.assertFalse(self.audit(blob='0'*40)['checks']['exact_github_html_blob'])

    def test_wrong_receipt_source_sha_fails(self):
        self.assertFalse(self.audit(lambda r:r.update(source_sha256='0'*64))['checks']['receipt_matches_html'])

    def test_no_exact_source_identity_fails(self):
        self.assertFalse(self.audit(lambda r:r.update(source_identity='UNCHECKED'))['checks']['source_gate'])

    def test_false_complete_cannot_bypass_missing_axe(self):
        def change(r): r.update(complete=True, axe_scans=[])
        self.assertEqual(self.audit(change)['classification'], 'BROWSER_PARTIAL_AXE_REQUIRED')

    def test_screenshot_tamper_fails(self):
        self.assertFalse(self.audit(lambda r:r['screenshots'].update({'R113_WEB_390.png':'0'*64}))['checks']['screenshots_sha256'])

    def test_missing_responsive_width_fails(self):
        self.assertFalse(self.audit(lambda r:r['modes'].pop())['checks']['full_responsive_matrix'])

    def test_nan_lcp_fails(self):
        self.assertFalse(self.audit(lambda r:r['performance'][0].update(lcp_ms=float('nan')))['checks']['six_lab_performance_trials'])

    def test_cls_budget_fails(self):
        self.assertFalse(self.audit(lambda r:r['performance'][1].update(cls=0.2))['checks']['six_lab_performance_trials'])

    def test_zero_violations_without_rule_execution_fails(self):
        def change(r):
            r['axe_scans'] = [{'width':w,'state':st,'violations':0,'ids':[]}
                              for w in (390,1440) for st in ('all','limit')]
        self.assertFalse(self.audit(change)['checks']['axe_four_unambiguous_scans'])

    def test_axe_manual_review_incomplete_blocks(self):
        self.assertFalse(self.audit(lambda r:r['axe_scans'][0].update(incomplete=1))['checks']['axe_four_unambiguous_scans'])

    def test_actual_chromium_receipt_only_when_supplied(self):
        path = os.environ.get('FV_APOLLO_RECEIPT')
        if not path: self.skipTest('Real browser receipt not supplied; NO browser PASS claimed')
        expected = os.environ.get('FV_APOLLO_GITHUB_BLOB')
        if not expected: self.fail('FV_APOLLO_GITHUB_BLOB must be provided')
        result = assess(Path(path), expected, ROOT)
        self.assertEqual(result['classification'], 'BROWSER_PARTIAL_AXE_REQUIRED')
        self.assertTrue(all(v for k,v in result['checks'].items() if k!='axe_four_unambiguous_scans'))

if __name__ == '__main__':
    unittest.main()
