"""R24 historical-source and campaign-integrity regression for the edited issue 02."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / 'issues/02-before-hypnosis-had-a-name.md').read_text(encoding='utf8')
MANIFEST = json.loads((ROOT / 'manifest.json').read_text(encoding='utf8'))

class PuysegurEvidenceGuards(unittest.TestCase):
    def test_01_campaign_still_4_2(self):
        self.assertEqual(len(MANIFEST['issues']), 6)
        self.assertEqual(sum(i['kind'] == 'editorial' for i in MANIFEST['issues']), 4)
        self.assertEqual(sum(i['kind'] == 'commercial-review-pending' for i in MANIFEST['issues']), 2)
        self.assertTrue(all(i['publish_state'] == 'hold' and i['merchant_affiliate_url'] is None for i in MANIFEST['issues']))

    def test_02_metadata_consistent(self):
        item = MANIFEST['issues'][1]
        self.assertEqual(item['kind'], 'editorial')
        self.assertIn('**Subject:** ' + item['subject'], SOURCE)
        self.assertIn('**Preheader:** ' + item['preheader'], SOURCE)
        self.assertLessEqual(len(item['subject']), 55)
        self.assertLessEqual(len(item['preheader']), 90)

    def test_03_historical_date_is_attested(self):
        self.assertIn('May 4, 1784', SOURCE)
        self.assertIn('Buzancy', SOURCE)
        self.assertIn('Victor Race', SOURCE)

    def test_04_testimony_not_trumped_as_proof(self):
        self.assertRegex(SOURCE, r'According to the account Puységur later published')
        self.assertIn('reportedly remembered nothing', SOURCE)
        self.assertIn('not', SOURCE)
        self.assertIn('testimony', SOURCE)

    def test_05_royal_commission_is_not_misrepresented(self):
        self.assertIn('not a direct test of Puységur', SOURCE)
        self.assertIn('commissioners', SOURCE)
        self.assertIn('proposed magnetic fluid', SOURCE)

    def test_06_scholarly_and_archive_links(self):
        for u in ('https://wellcomecollection.org/works/es4ayp6q',
                  'https://pubmed.ncbi.nlm.nih.gov/31273811/',
                  'https://pubmed.ncbi.nlm.nih.gov/8209564/'):
            self.assertIn(u, SOURCE)
        self.assertIn('not presently available for online examination', SOURCE)

    def test_07_reader_gets_substantive_value(self):
        for x in ('**Recorded:**','**Inferred:**','**Unsettled:**'):
            self.assertIn(x, SOURCE)

    def test_08_single_primary_cta(self):
        u = MANIFEST['issues'][1]['editorial_cta']
        self.assertEqual(SOURCE.count('](' + u + ')'), 1)
        self.assertTrue(u.startswith('https://finalvestige.com/'))
        self.assertTrue(SOURCE.index('**Read the file:**') < SOURCE.index('**Pre-send compliance block'))

    def test_09_no_commerce_or_tracked_urls(self):
        for value in ('affiliates.inspire3', 'clickbank', 'utm_', 'ref=', 'buy now', 'discount', 'earn a commission'):
            self.assertNotIn(value, SOURCE.lower())

    def test_10_postal_unsub_and_unsent_hold(self):
        for value in ('UNSENT DRAFT', '[[VALID_POSTAL_ADDRESS_REQUIRED]]',
                     '[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]'):
            self.assertIn(value, SOURCE)

    def test_11_all_hyperlinks_https(self):
        urls = re.findall(r'\]\(([^)]+)\)', SOURCE)
        self.assertGreaterEqual(len(urls), 4)
        self.assertTrue(all(u.startswith('https://') for u in urls))

    def test_12_avoids_medical_promise(self):
        self.assertIn('as medical evidence', SOURCE)
        self.assertNotIn('will cure', SOURCE.lower())
        self.assertNotIn('proves hypnosis works', SOURCE.lower())

if __name__ == '__main__':
    unittest.main()
