"""R26 regression audit of UNSENT Total Focus review. This never sends, publishes or connects."""
from pathlib import Path
import unittest
import json
import re

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
SOURCE = (ROOT/'issues/05-before-you-press-play.md').read_text(encoding='utf-8')
HTML = (ROOT/'previews/05-before-you-press-play.html').read_text(encoding='utf-8')
TEXT = (ROOT/'previews/05-before-you-press-play.txt').read_text(encoding='utf-8')
RECORD = MANIFEST['issues'][4]
CONTENT = SOURCE.split('\n---\n', 1)[1].split('\n---\n', 1)[0]

class R26TotalFocusTruth(unittest.TestCase):
    def test_01_manifest_4_2_preserved(self):
        self.assertEqual([i['kind'] for i in MANIFEST['issues']].count('editorial'), 4)
        self.assertEqual([i['kind'] for i in MANIFEST['issues']].count('commercial-review-pending'), 2)
    def test_02_six_issues(self): self.assertEqual(len(MANIFEST['issues']), 6)
    def test_03_order(self): self.assertEqual([i['number'] for i in MANIFEST['issues']], list(range(1,7)))
    def test_04_hold_every_issue(self): self.assertTrue(all(i['publish_state']=='hold' for i in MANIFEST['issues']))
    def test_05_no_affiliate_urls(self): self.assertTrue(all(i['merchant_affiliate_url'] is None for i in MANIFEST['issues']))
    def test_06_new_preheader_sync(self): self.assertIn('**Preheader:** '+RECORD['preheader'], SOURCE)
    def test_07_title_sync(self): self.assertIn('**Subject:** '+RECORD['subject'], SOURCE)
    def test_08_subject_honesty(self): self.assertLessEqual(len(RECORD['subject']), 65)
    def test_09_preheader_legibility(self): self.assertLessEqual(len(RECORD['preheader']), 100)
    def test_10_primary_cta_occurs_once(self): self.assertEqual(CONTENT.count(RECORD['editorial_cta']), 1)
    def test_11_commercial_disclosure_precedes_cta(self): self.assertLess(SOURCE.index('**Commercial disclosure:**'), SOURCE.index('**Review the Total Focus evidence'))
    def test_12_disclosure_close_to_cta(self): self.assertLess(SOURCE.index('**Review the Total Focus evidence')-SOURCE.index('**Commercial disclosure:**'), 510)
    def test_13_specific_seller_format(self):
        for s in (SOURCE,HTML,TEXT):
            self.assertIn('33 minutes',s);self.assertIn('47 MB',s)
    def test_14_seller_status_not_independent_proof(self):
        self.assertIn('seller claims',CONTENT.lower())
        self.assertIn('not independently verified',CONTENT.lower())
    def test_15_no_unproven_guarantee(self): self.assertNotRegex(CONTENT, r'(?i)\bguaranteed?\b.*(?:result|focus|success)')
    def test_16_no_evergreen_price(self):
        self.assertNotRegex(CONTENT, r'\$\s*\d')
        self.assertNotRegex(CONTENT, r'\b\d{1,3}%\s*off\b')
    def test_17_no_evergreen_refund_term(self): self.assertNotRegex(CONTENT, r'\b(?:14|30|365)[ -]day\s+(?:refund|guarantee)')
    def test_18_nihs_scope_limited(self):
        self.assertIn('https://www.nccih.nih.gov/health/hypnosis',SOURCE)
        self.assertIn('does not validate this commercial concentration recording',SOURCE)
    def test_19_research_not_product_effect(self): self.assertIn('product-specific',SOURCE)
    def test_20_free_observation(self):
        self.assertIn('A three-minute check you can do for free',SOURCE)
        self.assertIn('not a clinical attention score',SOURCE)
    def test_21_safety_not_driving(self): self.assertIn('not while driving or operating machinery',SOURCE)
    def test_22_free_offer_available(self): self.assertIn('https://finalvestige.com/focus/',SOURCE)
    def test_23_no_direct_merchant_outbound(self):
        for s in (SOURCE,HTML,TEXT):
            self.assertNotIn('https://hypnosislive.com/',s)
            self.assertNotRegex(s,r'(?i)utm_source=|aff_id=|clickbank')
    def test_24_static_preview_not_email(self):
        self.assertIn('NOT A SENT EMAIL',HTML)
        self.assertIn('UNSENT DRAFT',TEXT)
    def test_25_guide_never_active(self):
        self.assertNotIn('href="[[APPROVED_',HTML)
        self.assertIn('APPROVED_HYPNOSIS_LIVE_WARMUP_GUIDE_URL_REQUIRED',HTML)
    def test_26_legal_holds(self):
        for s in (SOURCE,TEXT):
            self.assertIn('[[VALID_POSTAL_ADDRESS_REQUIRED]]',s)
            self.assertIn('[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]',s)
    def test_27_plain_and_html_disclosure(self):
        for s in (HTML,TEXT):self.assertIn('Commercial disclosure:',s)
    def test_28_no_marketing_fake_results(self):
        self.assertNotRegex(CONTENT,r'(?i)\b(?:our readers|we tested|we measured|we achieved)\b')
    def test_29_one_review_placeholder(self):
        self.assertEqual(CONTENT.count('[[APPROVED_'),1)
    def test_30_active_other_editorial_untouched(self):
        self.assertEqual([i['number'] for i in MANIFEST['issues'] if i['kind']=='editorial'],[1,2,4,6])

if __name__=='__main__':unittest.main()
