"""Fail-closed ABBA verification tests with synthetic data. No network/CMS access."""
import unittest
from assess_css_abba import adjudicate, SEQUENCE, IMAGE_PATHS

HEAD = '7cd762501880d86e955a138e3ec60d48d5dda549'
PNG = b'\x89PNG\r\n\x1a\nsynthetic'


def fixture():
    records = []
    for i, v in enumerate(SEQUENCE, 1):
        samples = []
        for j in range(2):
            samples.append({'profile': f'mobile_390_trial_{j+1}', 'viewport': 390,
                            'cpu_slowdown_x': 4, 'network': '150ms_RTT_1.6Mbps',
                            'http_status': 200, 'chapters': 7, 'cache': 'disabled',
                            'instrumentation_failed': False, 'failure_codes': [],
                            'lcp_ms': 3200 if v == 'early' else 4100, 'cls': 0.02,
                            'page_timing_ms': {'fcp': 2400}})
        samples.append({'profile': 'desktop_1440', 'viewport': 1440, 'cpu_slowdown_x': 1,
                        'http_status': 200, 'chapters': 7, 'cache': 'disabled',
                        'instrumentation_failed': False, 'failure_codes': [],
                        'lcp_ms': 1100, 'cls': 0})
        records.append({'sequence': i, 'variant': v, 'screenshot': IMAGE_PATHS[i-1],
                        'saved_content_sha256': ('a' if v == 'early' else 'b')*64,
                        'lab_budget_gate': 'FAIL', 'samples': samples})
    return {'source_sha': HEAD, 'sequence': 'ABBA', 'release_gate': 'HOLD',
            'production_writes': False,
            'environment': 'DISPOSABLE_LOCAL_WORDPRESS_SAVED_GUTENBERG',
            'field_cwv': 'NOT_MEASURED', 'hosted_wordpress_com': 'NOT_TESTED',
            'records': records}


class ABBAAdjudicationTests(unittest.TestCase):
    def assessment(self, receipt=None, imgs=None):
        return adjudicate(fixture() if receipt is None else receipt,
                          [PNG]*4 if imgs is None else imgs, HEAD)

    def test_sample_reports_honest_hold_not_performance_pass(self):
        result = self.assessment()
        self.assertEqual(result['observed_lcp_delta_ms'], 900)
        self.assertEqual(result['early_mobile_lcp_budget_2500ms'], 'FAIL')
        self.assertEqual(result['release_decision'], 'HOLD')
        self.assertFalse(result['causal_proof'])

    def test_bad_source_sha_rejected(self):
        x = fixture(); x['source_sha'] = '1'*40
        with self.assertRaises(ValueError): self.assessment(x)

    def test_changed_sequence_rejected(self):
        x = fixture(); x['records'][1]['variant'] = 'early'
        with self.assertRaises(ValueError): self.assessment(x)

    def test_missing_trial_rejected(self):
        x = fixture(); x['records'][2]['samples'].pop()
        with self.assertRaises(ValueError): self.assessment(x)

    def test_bad_mobile_profile_rejected(self):
        x = fixture(); x['records'][0]['samples'][0]['viewport'] = 1440
        with self.assertRaises(ValueError): self.assessment(x)

    def test_broken_browser_rejected(self):
        x = fixture(); x['records'][1]['samples'][1]['http_status'] = 403
        with self.assertRaises(ValueError): self.assessment(x)

    def test_instrumentation_failure_rejected(self):
        x = fixture(); x['records'][0]['samples'][0]['instrumentation_failed'] = True
        with self.assertRaises(ValueError): self.assessment(x)

    def test_nonfinite_or_boolean_lcp_rejected(self):
        for bad in (float('nan'), float('inf'), True, None, '3200'):
            x = fixture(); x['records'][0]['samples'][0]['lcp_ms'] = bad
            with self.subTest(bad=bad), self.assertRaises(ValueError): self.assessment(x)

    def test_untrusted_hosted_claim_rejected(self):
        x = fixture(); x['hosted_wordpress_com'] = 'PASS'
        with self.assertRaises(ValueError): self.assessment(x)

    def test_undisclosed_production_writes_rejected(self):
        x = fixture(); x['production_writes'] = True
        with self.assertRaises(ValueError): self.assessment(x)

    def test_changed_screenshot_rejected(self):
        imgs = [PNG]*4; imgs[2] = PNG+b'changed'
        with self.assertRaises(ValueError): self.assessment(imgs=imgs)

    def test_early_payload_drift_rejected(self):
        x = fixture(); x['records'][-1]['saved_content_sha256'] = 'f'*64
        with self.assertRaises(ValueError): self.assessment(x)

    def test_performance_budget_pass_not_release_permission(self):
        x = fixture()
        for r in x['records']:
            if r['variant'] == 'early':
                for s in r['samples'][:2]: s['lcp_ms'] = 2400
        result = self.assessment(x)
        self.assertEqual(result['early_mobile_lcp_budget_2500ms'], 'PASS')
        self.assertEqual(result['release_decision'], 'HOLD')

    def test_no_cwv_fabrication(self):
        x = fixture(); x['field_cwv'] = 'PASS'
        with self.assertRaises(ValueError): self.assessment(x)


if __name__ == '__main__':
    unittest.main()
