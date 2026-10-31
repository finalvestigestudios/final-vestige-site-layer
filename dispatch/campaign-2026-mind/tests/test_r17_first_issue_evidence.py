"""R17: exact-route and experiment/evidence safeguards for UNSENT first edition.

These checks do not confer approval to publish, contact subscribers, or send email.
"""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
ONE = ROOT / 'issues/01-the-mind-is-not-a-camera.md'
TWO = ROOT / 'issues/02-before-hypnosis-had-a-name.md'

class FirstIssueProof(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.body = ONE.read_text(encoding='utf-8')
        cls.second = TWO.read_text(encoding='utf-8')
        cls.manifest = json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))
        cls.one = cls.manifest['issues'][0]
        cls.two = cls.manifest['issues'][1]

    def test_exact_study_attribution(self):
        for term in ['Simons', 'Levin', '1998', '10.3758/BF03208840', 'field experiment']:
            self.assertIn(term, self.body)

    def test_no_exaggeration_from_single_sample(self):
        for term in ['about half', 'studied conditions', 'not a universal percentage', 'doesn\'t prove']:
            self.assertIn(term, self.body)
        self.assertNotIn('all eyewitnesses', self.body.lower())

    def test_archive_claim_bound_to_live_first_party_resource(self):
        self.assertIn('four linked records', self.body)
        self.assertIn('https://finalvestige.com/the-missing-caption/', self.body)
        self.assertEqual(self.one['editorial_cta'], 'https://finalvestige.com/the-missing-caption/')

    def test_main_cta_not_recycled_next_week(self):
        self.assertNotEqual(self.one['editorial_cta'], self.two['editorial_cta'])
        self.assertIn('puysegurs-animal-magnetism-files', self.two['editorial_cta'])
        self.assertNotIn('puysegurs-animal-magnetism-files', self.body)

    def test_subject_and_preheader_match_manifest(self):
        self.assertIn('**Subject:** ' + self.one['subject'], self.body)
        self.assertIn('**Preheader:** ' + self.one['preheader'], self.body)

    def test_email_safety_markers_remain(self):
        for token in ['UNSENT DRAFT', '[[VALID_POSTAL_ADDRESS_REQUIRED]]',
                      '[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]']:
            self.assertIn(token,self.body)

    def test_no_commercial_content_or_merchant_tracking(self):
        for term in ['inspire3.com','zen12.com','hypnosislive.com','utm_','aff_id=','buy now']:
            self.assertNotIn(term,self.body.lower())
        self.assertEqual(self.one['kind'],'editorial')
        self.assertIsNone(self.one['merchant_affiliate_url'])

    def test_evidence_first_practical_value(self):
        for term in ['**Describe:**','**Separate:**','**Check:**','hypotheses']:
            self.assertIn(term,self.body)
        copy = self.body.split('\n---\n')[1]
        self.assertGreaterEqual(len(copy.split()), 260)
        self.assertLessEqual(len(copy.split()), 480)

    def test_attribution_link_not_conversion_cta(self):
        links=re.findall(r'\]\((https://[^)]+)\)',self.body)
        self.assertEqual(set(links),{'https://finalvestige.com/the-missing-caption/', 'https://doi.org/10.3758/BF03208840'})

    def test_wordpress_subscriber_semantics_not_stale(self):
        live=self.manifest['verified_live_site']
        self.assertNotIn('count_discrepancy',live)
        self.assertIn('unconfirmed excluded from total',live['subscriber_semantics'])
        self.assertIn('unverified',live['subscriber_semantics'])

    def test_preview_regenerated_exactly(self):
        # Compare source paragraphs with generated HTML and text, not actual Jetpack email.
        html=(ROOT/'previews/01-the-mind-is-not-a-camera.html').read_text()
        txt=(ROOT/'previews/01-the-mind-is-not-a-camera.txt').read_text()
        for token in ['The Missing Caption','Simons and Levin','studied conditions']:
            self.assertIn(token,html)
            self.assertIn(token,txt)
        self.assertIn(self.one['preheader'],html)
        self.assertIn('NOT A SENT EMAIL',html)
        self.assertIn('[[VALID_POSTAL_ADDRESS_REQUIRED]]',txt)

    def test_six_still_hold_four_to_two(self):
        entries=self.manifest['issues']
        self.assertEqual(len(entries),6)
        self.assertEqual(sum(e['kind']=='editorial' for e in entries),4)
        self.assertEqual(sum(e['kind']=='commercial-review-pending' for e in entries),2)
        self.assertTrue(all(e['publish_state']=='hold' for e in entries))
        self.assertTrue(all(e['merchant_affiliate_url'] is None for e in entries))

if __name__=='__main__':
    unittest.main()
