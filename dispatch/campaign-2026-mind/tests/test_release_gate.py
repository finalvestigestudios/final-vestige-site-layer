"""Dependency-free verification of the read-only Dispatch release gate."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from release_gate import REQUIRED_EVIDENCE, inspect


class ReleaseGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'issues').mkdir()
        self.entries = []
        for n in range(1, 7):
            kind = 'commercial-review-pending' if n in (3, 5) else 'editorial'
            token = ('[[APPROVED_ZEN12_WARMUP_GUIDE_URL_REQUIRED]]' if n == 3 else
                     '[[APPROVED_HYPNOSIS_LIVE_WARMUP_GUIDE_URL_REQUIRED]]' if n == 5 else 'https://finalvestige.com/focus/')
            item = dict(number=n, slug=f'sample-{n}', subject=f'Subject {n}', preheader=f'Preview {n}',
                        kind=kind, publish_state='hold', merchant_affiliate_url=None, editorial_cta=token)
            self.entries.append(item)
            md = (f'# TEST\n> UNSENT DRAFT\n**Subject:** Subject {n}\n**Preheader:** Preview {n}\n'
                  f'**Commercial disclosure:** Final Vestige may earn a commission.\nGo: {token}\n'
                  '[[VALID_POSTAL_ADDRESS_REQUIRED]] [[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]')
            (self.root / 'issues' / f'{n:02d}-sample-{n}.md').write_text(md, encoding='utf-8')
        self.manifest = {'status': 'DRAFT_UNSENT_NO_SCHEDULING', 'id': 'test-campaign', 'issues': self.entries}
        self.att = {'checks': {key: {'verified': False, 'evidence_reference': None} for key in REQUIRED_EVIDENCE}}

    def evaluate(self):
        return inspect(self.manifest, self.att, self.root)

    def test_default_fails_closed(self):
        r = self.evaluate()
        self.assertEqual(r['status'], 'BLOCKED')
        self.assertEqual(len(r['blocking_evidence_gates']), len(REQUIRED_EVIDENCE))
        self.assertFalse(r['ready_to_send'])
        self.assertFalse(r['structural_errors'])

    def test_all_evidence_passes_only_to_review(self):
        for value in self.att['checks'].values():
            value.update(verified=True, evidence_reference='internal-review-ticket-123')
        r = self.evaluate()
        self.assertEqual(r['status'], 'REVIEW_READY_NOT_AUTHORIZED_TO_SEND')
        self.assertFalse(r['ready_to_send'])

    def test_missing_proof_fails_closed(self):
        self.att['checks']['deduplicated_confirmed_consent'] = {'verified': True}
        self.assertIn('deduplicated_confirmed_consent:missing_proof_reference', self.evaluate()['blocking_evidence_gates'])

    def test_held_source_and_metadata_cannot_be_silently_released(self):
        self.entries[0]['publish_state'] = 'publish'
        self.assertIn('01-sample-1:not_explicitly_held', self.evaluate()['structural_errors'])

    def test_product_destination_cannot_be_substituted(self):
        self.entries[2]['editorial_cta'] = 'https://zen12.com/'
        self.assertIn('03-sample-3:commercial_guide_not_safely_blocked', self.evaluate()['structural_errors'])

    def test_undeclared_seller_affiliate_url_is_error(self):
        self.entries[2]['merchant_affiliate_url'] = 'https://example.com/affiliate'
        self.assertIn('unexpected_active_merchant_affiliate_url', self.evaluate()['structural_errors'])

    def test_disclosure_must_precede_commercial_cta(self):
        path = self.root / 'issues' / '05-sample-5.md'
        text = path.read_text()
        text = text.replace('**Commercial disclosure:** Final Vestige may earn a commission.\nGo:', 'Go:')
        path.write_text(text + '\n**Commercial disclosure:** Final Vestige may earn a commission.', encoding='utf-8')
        self.assertIn('05-sample-5:commercial_disclosure_not_before_cta', self.evaluate()['structural_errors'])

    def test_legal_placeholders_required(self):
        path = self.root / 'issues' / '01-sample-1.md'
        path.write_text(path.read_text().replace('[[VALID_POSTAL_ADDRESS_REQUIRED]]', 'Unverified office'))
        self.assertIn('01-sample-1:postal_hold_missing', self.evaluate()['structural_errors'])

    def test_correct_issue_ratio_required(self):
        self.entries[0]['kind'] = 'commercial-review-pending'
        self.assertIn('campaign_must_remain_four_editorial_two_commercial_review', self.evaluate()['structural_errors'])

    def test_no_automatic_send_action(self):
        self.assertFalse(self.evaluate()['site_writes_or_emails_performed'])


if __name__ == '__main__':
    unittest.main()
