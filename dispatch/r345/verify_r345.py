"""Offline editorial safeguards; passing is never authority to send."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parent
MD = (ROOT / 'issue03-zen12-alternative.md').read_text(encoding='utf-8')
TXT = (ROOT / 'issue03-zen12-alternative.txt').read_text(encoding='utf-8')
HTML = (ROOT / 'issue03-zen12-alternative.html').read_text(encoding='utf-8')
EVIDENCE = (ROOT / 'PRODUCT_EVIDENCE_AND_PERMISSION_MATRIX.md').read_text(encoding='utf-8')
RELEASE = (ROOT / 'NATIVE_PREVIEW_CONSENT_AND_CONVERSION.md').read_text(encoding='utf-8')

class ReviewGuards(unittest.TestCase):
    def test_optional_not_adopted(self):
        for s in (MD, TXT, HTML):
            self.assertRegex(s, r'(?i)(NOT ADOPTED|NOT A WORDPRESS EMAIL PREVIEW)')
    def test_placeholder_stops_all_formats(self):
        for s in (MD, TXT, HTML):
            for token in ('[[VALID_POSTAL_ADDRESS_REQUIRED]]', '[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]'):
                self.assertIn(token, s)
    def test_no_merchant_link_enabled(self):
        self.assertNotIn('affiliates.inspire3.com', MD + TXT + HTML)
        self.assertNotRegex(HTML, r'href=["\']\[\[APPROVED_')
    def test_one_primary_cta(self):
        self.assertEqual(MD.count('**Primary CTA'), 1)
        self.assertEqual(TXT.count('PRIMARY CTA'), 1)
    def test_disclosure_near_candidate(self):
        self.assertLess(MD.index('**Commercial disclosure'), MD.index('**Evidence and further reading'))
        self.assertLess(MD.index('**Commercial disclosure') - MD.index('**Primary CTA'), 850)
    def test_supporting_sources_specific(self):
        for s in (MD, TXT, HTML):
            self.assertIn('37205669', s)
            self.assertIn('35842538', s)
    def test_no_equivalence_as_assertion(self):
        self.assertIn('do **not** establish', MD)
        self.assertIn('Neither review tested Zen12 itself', HTML)
    def test_email_markup_safe(self):
        self.assertIn('lang="en"', HTML)
        self.assertIn('role="presentation"', HTML)
        self.assertEqual(HTML.count('<h1'), 1)
        self.assertNotRegex(HTML.lower(), r'<(script|form|iframe|video)|onclick=|autoplay|javascript:')
    def test_preheader_limitation(self):
        self.assertIn('not a verified Jetpack field', MD)
        self.assertIn('NOT A VERIFIED FIELD', RELEASE)
    def test_consent_not_download(self):
        self.assertIn('not a delivered-email receipt', RELEASE)
        self.assertIn('not yet measured', RELEASE)
    def test_conversion_not_clicks(self):
        self.assertIn('not sales', RELEASE)
        self.assertIn('NOT COMPUTABLE', RELEASE)
    def test_commercial_permission_absent(self):
        self.assertIn('EMAIL_RIGHTS=FALSE', EVIDENCE)
        self.assertIn('GUIDE_LIVE_APPROVED=FALSE', EVIDENCE)
    def test_six_edition_mix(self):
        self.assertEqual(sum(f'| 0{i} |' in RELEASE for i in range(1, 7)), 6)
        self.assertEqual(RELEASE.count('| Commercial ('), 2)
    def test_absence_of_false_metric(self):
        self.assertNotRegex(MD + TXT, r'(?i)we (measured|sold|earned) [0-9]+')

if __name__ == '__main__':
    unittest.main()
