import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent

class Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.scripts = 0
        self.images = 0
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.links.append(dict(attrs).get('href', ''))
        if tag == 'script':
            self.scripts += 1
        if tag == 'img':
            self.images += 1

class CampaignR283(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.md = (ROOT / 'issue03_review.md').read_text(encoding='utf8')
        cls.plain = (ROOT / 'issue03_plain.txt').read_text(encoding='utf8')
        cls.html = (ROOT / 'reviewer_preview.html').read_text(encoding='utf8')
        cls.truth = (ROOT / 'funnel_truth_table.md').read_text(encoding='utf8')
        cls.gates = json.loads((ROOT / 'claims_and_gates.json').read_text(encoding='utf8'))
    def test_slot(self):
        self.assertEqual(self.gates['issue_slot'], 3)
    def test_mix_unchanged(self):
        self.assertIn('original 4 editorial / 2 reserved commercial', self.md)
    def test_not_adopted(self):
        self.assertEqual(self.gates['candidate'], 'review_only_not_adopted')
    def test_no_release(self):
        self.assertEqual(self.gates['campaign_state'], 'HOLD_UNSENT')
    def test_merchant_hold(self):
        self.assertEqual(self.gates['merchant_state'], 'HOLD_MERCHANT')
    def test_all_boolean_approvals_false(self):
        for key, value in self.gates.items():
            if isinstance(value, bool):
                self.assertIs(value, False, key)
    def test_no_real_revenue(self):
        self.assertIsNone(self.gates['net_revenue_per_1000_human_sessions'])
    def test_subject_honest(self):
        subject = re.search(r'\*\*Subject:\*\* (.*)', self.md).group(1)
        self.assertLessEqual(len(subject), 60)
        self.assertNotRegex(subject.lower(), 'cure|guarantee|miracle|last chance')
    def test_preheader_honest(self):
        preheader = re.search(r'\*\*Preheader:\*\* (.*)', self.md).group(1)
        self.assertLessEqual(len(preheader), 120)
        self.assertNotIn('guaranteed', preheader.lower())
    def test_one_guide_cta(self):
        self.assertEqual(self.md.count('**One prospective guide CTA'), 1)
    def test_blocked_cta_all_renderings(self):
        for x in (self.md, self.plain, self.html):
            self.assertIn('[[APPROVED_LIVE_ZEN12_GUIDE_URL_REQUIRED]]', x)
    def test_near_link_disclosure(self):
        self.assertLess(self.md.index('**Commercial disclosure'), self.md.index('**Sources'))
    def test_no_active_merchant_link(self):
        self.assertNotRegex(self.md, r'(?i)https?://[^\s]+affiliate_id=')
    def test_inventory_seller_attributed(self):
        self.assertIn('48 MP3', self.md)
        self.assertIn("seller's inventory description", self.md)
    def test_research_source(self):
        self.assertIn('nccih.nih.gov', self.md)
    def test_official_offer_source(self):
        self.assertIn('zen12.com/getstarted', self.md)
    def test_price_omitted(self):
        self.assertNotRegex(self.md, r'\$\d')
    def test_no_firsthand_product_claim(self):
        self.assertNotIn('I tried Zen12', self.md)
    def test_postal_hold_all_renderings(self):
        for x in (self.md, self.plain, self.html):
            self.assertIn('[[VALID_POSTAL_ADDRESS_REQUIRED]]', x)
    def test_unsubscribe_hold_all_renderings(self):
        for x in (self.md, self.plain, self.html):
            self.assertIn('[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]', x)
    def test_html_no_remote_fetch(self):
        tags = Tags()
        tags.feed(self.html)
        self.assertEqual(tags.links, [])
        self.assertEqual(tags.scripts, 0)
        self.assertEqual(tags.images, 0)
    def test_html_basic_accessibility(self):
        self.assertIn('lang="en"', self.html)
        self.assertIn('name="viewport"', self.html)
        self.assertIn('<main ', self.html)
    def test_truth_pdf_not_lead(self):
        self.assertIn('not a recipient-confirmed lead', self.truth)
    def test_truth_not_additive(self):
        self.assertIn('cannot be added', self.truth)
    def test_truth_paid_only_from_merchant(self):
        self.assertIn('Merchant statement reports attributed settled order', self.truth)
    def test_truth_no_fake_kpi(self):
        self.assertIn('NOT COMPUTABLE', self.truth)
    def test_disclosure_in_plain_and_html(self):
        self.assertIn('may receive a commission', self.plain)
        self.assertIn('may receive a commission', self.html)
    def test_source_count(self):
        self.assertGreaterEqual(len(self.gates['sources']), 4)
    def test_no_duplicate_source(self):
        urls = [source['url'] for source in self.gates['sources']]
        self.assertEqual(len(urls), len(set(urls)))
    def test_non_sending_payload(self):
        for path in ROOT.glob('*'):
            if path.suffix in ('.html', '.md', '.txt', '.json'):
                body = path.read_text(encoding='utf8')
                self.assertNotIn('script src=', body)
                self.assertNotIn('smtp://', body)

if __name__ == '__main__':
    unittest.main()
