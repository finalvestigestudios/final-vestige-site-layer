"""R25: fail-closed offer-tier and email-safety checks (no network, no sends)."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = (ROOT / 'issues/03-the-twelve-minute-question.md').read_text(encoding='utf-8')
HTML = (ROOT / 'previews/03-the-twelve-minute-question.html').read_text(encoding='utf-8')
PLAIN = (ROOT / 'previews/03-the-twelve-minute-question.txt').read_text(encoding='utf-8')
BRIDGE = (ROOT / 'wordpress-post-bridge-r23/proofs/issue-03.blocks.html').read_text(encoding='utf-8')
MANIFEST = json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))
ITEM = MANIFEST['issues'][2]

class MerchantTierTruth(unittest.TestCase):
    def test_one_six_edition_four_two_campaign(self):
        self.assertEqual([i['number'] for i in MANIFEST['issues']], list(range(1,7)))
        self.assertEqual([i['kind'] for i in MANIFEST['issues']].count('commercial-review-pending'), 2)

    def test_two_all_hold_with_no_affiliate_urls(self):
        self.assertEqual(MANIFEST['status'], 'DRAFT_UNSENT_NO_SCHEDULING')
        self.assertTrue(all(i['publish_state']=='hold' and i['merchant_affiliate_url'] is None for i in MANIFEST['issues']))

    def test_three_correct_full_course_tier(self):
        self.assertIn('Premium package advertises twelve levels and 48 MP3 files', SRC)

    def test_four_limited_course_tiers_not_erased(self):
        self.assertIn('Beginner and Advanced packages each list six levels and 24 MP3s', SRC)

    def test_five_advertised_not_verified_effect(self):
        self.assertIn('not evidence that every buyer receives the full library', SRC)
        self.assertIn('not verified independent, product-specific comparative evidence', SRC)

    def test_six_official_sales_and_about_source_links(self):
        self.assertIn('[sales page](https://zen12.com/)', SRC)
        self.assertIn('[About page](https://zen12.com/about)', SRC)

    def test_seven_no_sales_price_or_refund_promise(self):
        body = SRC.split('\n---\n',1)[1]
        self.assertNotRegex(body, r'\$\s*\d')
        self.assertNotRegex(body, r'\b(14|30|365)[- ]day\s+refund')

    def test_eight_timer_does_not_create_fake_deadline(self):
        self.assertIn('A checkout may ask for a **mobile number**', SRC)
        self.assertIn('A timer alone is not independent evidence', SRC)
        self.assertNotIn('checkout currently requests a mobile number', SRC)

    def test_nine_free_exercise_survives(self):
        for x in ('**One minute:**','**Nine minutes:**','**Two minutes:**','before you buy anything'):
            self.assertIn(x, SRC)

    def test_ten_subject_and_preheader_unchanged(self):
        self.assertIn('**Subject:** '+ITEM['subject'], SRC)
        self.assertIn('**Preheader:** '+ITEM['preheader'], SRC)

    def test_eleven_near_offer_disclosure_still_visible(self):
        a=SRC.index('**Commercial disclosure:**'); b=SRC.index('[[APPROVED_ZEN12_WARMUP_GUIDE_URL_REQUIRED]]')
        self.assertLess(a,b)
        self.assertLess(b-a,950)

    def test_twelve_guide_cta_remains_dead_and_unique(self):
        self.assertEqual(SRC.count('[[APPROVED_ZEN12_WARMUP_GUIDE_URL_REQUIRED]]'),1)
        self.assertIn('GUIDE NOT LIVE — NO LINK',BRIDGE)
        self.assertNotRegex(BRIDGE,r'href="[^"]*(?:aff_id|clickbank|affiliates\.inspire3)')

    def test_thirteen_rendered_tier_wording_matches(self):
        for out in (HTML,PLAIN,BRIDGE):
            self.assertIn('Premium package advertises twelve levels and 48 MP3 files',out)
            self.assertIn('Beginner and Advanced packages each list six levels and 24 MP3s',out)

    def test_fourteen_no_placeholders_become_active_merchant_links(self):
        self.assertNotIn('href="[[APPROVED_',HTML)
        self.assertNotIn('href="[[APPROVED_',BRIDGE)
        self.assertNotIn('merchant_affiliate_url": "https', json.dumps(MANIFEST))

    def test_fifteen_legal_proof_still_required(self):
        self.assertIn('[[VALID_POSTAL_ADDRESS_REQUIRED]]',SRC)
        self.assertIn('[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]',SRC)
        self.assertIn('NOT A SENT EMAIL',HTML)

    def test_sixteen_no_false_merchant_authorization(self):
        self.assertIn('We have not verified our affiliate approval or permission',SRC)
        self.assertNotIn('our approved affiliate link',SRC.lower())

    def test_seventeen_no_unverifiable_outcomes(self):
        for term in ('guaranteed brainwave results','clinically proven zen12','we tested zen12','zen12 cures'):
            self.assertNotIn(term,SRC.lower())

    def test_eighteen_one_identifiable_primary_guide_action(self):
        self.assertEqual(SRC.count('**Read our independent Zen12 evaluation'),1)
        self.assertEqual(ITEM['editorial_cta'],'[[APPROVED_ZEN12_WARMUP_GUIDE_URL_REQUIRED]]')

if __name__ == '__main__': unittest.main()
