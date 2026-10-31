"""R20: source-led Zen12 edition integrity. Pure read-only local regression tests."""
import json
import pathlib
import re
import subprocess
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
ISSUE = ROOT / 'issues' / '03-the-twelve-minute-question.md'
HTML = ROOT / 'previews' / '03-the-twelve-minute-question.html'
TEXT = ROOT / 'previews' / '03-the-twelve-minute-question.txt'
MANIFEST = ROOT / 'manifest.json'


class Zen12R20Guards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = ISSUE.read_text(encoding='utf-8')
        cls.html = HTML.read_text(encoding='utf-8')
        cls.text = TEXT.read_text(encoding='utf-8')
        cls.manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
        cls.entry = next(i for i in cls.manifest['issues'] if i['number'] == 3)
        cls.body = cls.source.split('\n---\n')[1]

    def test_01_preserves_original_subject_and_preheader(self):
        self.assertIn('**Subject:** ' + self.entry['subject'], self.source)
        self.assertIn('**Preheader:** ' + self.entry['preheader'], self.source)

    def test_02_content_classification_and_split(self):
        self.assertIn('**Content type:** commercial-review-pending', self.source)
        kinds = [i['kind'] for i in self.manifest['issues']]
        self.assertEqual(kinds.count('editorial'), 4)
        self.assertEqual(kinds.count('commercial-review-pending'), 2)

    def test_03_product_specific_inventory(self):
        for term in ('twelve levels', '48 MP3 files', 'four listening styles',
                     'guided meditation', 'relaxation music', 'white noise', 'nature sounds'):
            self.assertIn(term, self.source)

    def test_04_inventory_attributed_to_seller(self):
        self.assertIn('Its official [sales page](https://zen12.com/) and [About page](https://zen12.com/about)', self.source)
        self.assertIn('checkable descriptions', self.source)

    def test_05_time_equivalence_separated_from_product_proof(self):
        self.assertIn("benefits of an hour's meditation", self.source)
        self.assertIn('not verified independent, product-specific comparative evidence', self.source)

    def test_06_brain_state_advertising_not_endorsed(self):
        self.assertIn('audio automatically shifts brain states', self.source)
        self.assertIn('those assertions', self.source)
        self.assertNotIn('Zen12 automatically shifts your brain state', self.source)

    def test_07_nih_not_transferred_to_sku(self):
        self.assertIn('https://www.nccih.nih.gov/health/meditation-and-mindfulness-effectiveness-and-safety', self.source)
        self.assertIn("cannot certify Zen12's advertised equivalence", self.source)

    def test_08_free_12_minute_test_is_arithmetically_honest(self):
        self.assertIn('**One minute:**', self.source)
        self.assertIn('**Nine minutes:**', self.source)
        self.assertIn('**Two minutes:**', self.source)
        self.assertIn('without special audio', self.source)
        self.assertIn('If you stopped early', self.source)

    def test_09_no_medical_claim_from_observation_log(self):
        self.assertIn('not a clinical measure or proof of improved concentration', self.source)
        self.assertIn('practice and fit', self.source)
        self.assertNotIn('guaranteed health', self.source.lower())

    def test_10_buyer_objections_cover_terms_and_data_fields(self):
        for term in ('current checkout and refund terms', 'mobile number', 'timed promotion'):
            self.assertIn(term, self.source)

    def test_11_merchant_permission_is_unverified(self):
        self.assertIn('have not verified our affiliate approval or permission', self.source)
        self.assertIn('not active', self.source)

    def test_12_disclosure_precedes_guide_placeholder(self):
        disclosure = self.body.find('**Commercial disclosure:**')
        offer = self.body.find('[[APPROVED_ZEN12_WARMUP_GUIDE_URL_REQUIRED]]')
        self.assertTrue(0 < disclosure < offer)
        self.assertLess(offer - disclosure, 950)

    def test_13_one_guide_cta_and_no_checkout_or_earning_link(self):
        self.assertEqual(self.body.count('[[APPROVED_ZEN12_WARMUP_GUIDE_URL_REQUIRED]]'), 1)
        self.assertEqual(self.body.count('**Read our independent Zen12 evaluation'), 1)
        self.assertNotIn('https://zen12.com/getstarted', self.body)
        self.assertNotIn('aff_id=', self.body)
        self.assertNotIn('utm_', self.body)
        self.assertIsNone(self.entry['merchant_affiliate_url'])

    def test_14_no_price_refund_duration_or_timer_deadline_promises(self):
        for pattern in (r'\$\d', r'\d+[- ]day money.back guarantee',
                        r'offer ends today', r'limited seats', r'50% off'):
            self.assertIsNone(re.search(pattern, self.body, re.I))

    def test_15_no_false_first_person_product_use(self):
        for term in ('i listened to zen12', 'we tested zen12', 'our measured improvement',
                     'our affiliates confirmed', 'we earned a commission'):
            self.assertNotIn(term, self.source.lower())

    def test_16_all_required_send_holds_remain(self):
        for item in ('UNSENT DRAFT', '[[VALID_POSTAL_ADDRESS_REQUIRED]]',
                     '[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]'):
            self.assertIn(item, self.source)
        self.assertEqual(self.entry['publish_state'], 'hold')

    def test_17_html_and_plaintext_are_review_only(self):
        self.assertIn('NOT A SENT EMAIL', self.html)
        self.assertIn('[UNVERIFIED: APPROVED_ZEN12_WARMUP_GUIDE_URL_REQUIRED]', self.html)
        self.assertNotIn('href="[[APPROVED_', self.html)
        self.assertIn('UNSENT DRAFT — DO NOT SEND', self.text)
        self.assertIn('[[APPROVED_ZEN12_WARMUP_GUIDE_URL_REQUIRED]]', self.text)
        self.assertNotIn('<script', self.html.lower())
        self.assertNotIn('<img', self.html.lower())

    def test_18_long_unverified_guide_tokens_have_email_safe_inline_wrap(self):
        self.assertIn('overflow-wrap:anywhere;word-break:break-all;', self.html)
        self.assertIn('[UNVERIFIED: APPROVED_ZEN12_WARMUP_GUIDE_URL_REQUIRED]', self.html)
        other = (ROOT / 'previews' / '05-before-you-press-play.html').read_text(encoding='utf-8')
        self.assertIn('overflow-wrap:anywhere;word-break:break-all;', other)
        self.assertIn('[UNVERIFIED: APPROVED_HYPNOSIS_LIVE_WARMUP_GUIDE_URL_REQUIRED]', other)

    def test_19_compatible_plaintext_does_not_embed_css_or_merchant_links(self):
        self.assertNotIn('word-break:', self.text)
        self.assertNotIn('https://zen12.com/getstarted', self.text)
        self.assertNotIn('utm_', self.text)
        self.assertIn('[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]', self.text)

    def test_20_renderer_matches_entire_campaign(self):
        completed = subprocess.run(['node', str(ROOT / 'tools' / 'build_previews.cjs'), '--check'],
                                   cwd=ROOT, capture_output=True, text=True, check=False)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertIn('13 files', completed.stdout)


if __name__ == '__main__':
    unittest.main()
