"""Native Python release tests of the original, non-sending excerpt specification."""
import copy
import json
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from verify_excerpt_contract import audit, render

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = json.loads((ROOT / 'excerpt_contract.json').read_text(encoding='utf-8'))


class GateTests(unittest.TestCase):
    def test_baseline(self):
        self.assertEqual(audit(DOC), [])

    def test_every_excerpt_below_320_characters(self):
        self.assertTrue(all(len(e['excerpt']) <= 320 for e in DOC['issues']))

    def test_commercial_cannot_omit_disclosure(self):
        for n in (3, 5):
            bad = copy.deepcopy(DOC)
            e = bad['issues'][n-1]
            e['excerpt'] = e['excerpt'].replace('Final Vestige may earn a commission', 'we recommend it')
            self.assertTrue(audit(bad))

    def test_false_partner_approval_blocked(self):
        bad = copy.deepcopy(DOC)
        bad['rules']['merchant_email_permission_verified'] = True
        self.assertTrue(audit(bad))

    def test_false_received_email_blocked(self):
        bad = copy.deepcopy(DOC)
        bad['rules']['actual_received_email_verified'] = True
        self.assertTrue(audit(bad))

    def test_live_merchant_link_blocked(self):
        bad = copy.deepcopy(DOC)
        bad['issues'][2]['in_post_destination'] = 'https://zen12.com/hnp?ref=surprise'
        self.assertTrue(audit(bad))

    def test_campaign_send_gate_blocked(self):
        bad = copy.deepcopy(DOC)
        bad['release'] = 'READY_TO_SEND'
        self.assertTrue(audit(bad))

    def test_publish_gate_blocked(self):
        bad = copy.deepcopy(DOC)
        bad['rules']['do_not_publish'] = False
        self.assertTrue(audit(bad))

    def test_postal_address_must_be_verified(self):
        bad = copy.deepcopy(DOC)
        bad['rules']['legal_postal_address_verified'] = True
        self.assertTrue(audit(bad))

    def test_wordpress_configuration_change_blocked(self):
        bad = copy.deepcopy(DOC)
        bad['rules']['email_content_format'] = 'full'
        self.assertTrue(audit(bad))

    def test_six_issue_composition_immutable(self):
        bad = copy.deepcopy(DOC)
        bad['issues'][3]['kind'] = 'commercial-review-pending'
        self.assertTrue(audit(bad))

    def test_apollo_title_qa_blocker_required(self):
        bad = copy.deepcopy(DOC)
        bad['issues'][3]['editorial_title_qa'] = 'PASS_CANDIDATE'
        self.assertTrue(audit(bad))

    def test_double_signup_link_blocked_for_issue_six(self):
        bad = copy.deepcopy(DOC)
        bad['issues'][5]['in_post_destination'] = 'https://finalvestige.com/focus/'
        self.assertTrue(audit(bad))

    def test_pii_and_pixel_blocked(self):
        for injected in (' user@example.com', ' https://tracking.example.net/pixel', ' utm_campaign=xyz'):
            bad = copy.deepcopy(DOC)
            bad['issues'][0]['excerpt'] += injected
            self.assertTrue(audit(bad))

    def test_banned_claims_blocked(self):
        for claim in (' guaranteed', ' cures anxiety', ' 100% effective'):
            bad = copy.deepcopy(DOC)
            bad['issues'][1]['excerpt'] += claim
            self.assertTrue(audit(bad))

    def test_render_is_static_and_six_cards(self):
        page = render(DOC)
        self.assertEqual(page.count('<article '), 6)
        for bad in ('<script', '<form', '<iframe', 'href="https://zen12', '<img', 'mailto:'):
            self.assertNotIn(bad, page)
        self.assertIn('<main>', page)
        self.assertIn('lang="en"', page)

    def test_source_ledgers(self):
        self.assertEqual(len(DOC['official_sources']), 7)
        self.assertIn('https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business', DOC['official_sources'])

    def test_actual_received_email_remains_unverified(self):
        self.assertFalse(DOC['rules']['actual_received_email_verified'])


if __name__ == '__main__':
    unittest.main()
