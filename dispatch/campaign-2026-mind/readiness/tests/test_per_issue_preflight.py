"""Adversarial and positive checks for the non-deployable edition-readiness gate."""
import copy
import importlib.util
import json
import pathlib
import unittest

BASE=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('per_issue_preflight',BASE/'per_issue_preflight.py')
gate=importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

def v():return {'verified': True,'reviewer_role':'Editor in chief','private_evidence_reference':'private-ticket:verification-1234'}

class EditionReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest=json.loads((BASE/'fixtures'/'manifest_snapshot.json').read_text(encoding='utf-8'))
        cls.ledger=json.loads((BASE/'canonical_cta_ledger.json').read_text(encoding='utf-8'))
        cls.att=json.loads((BASE/'edition_attestations.json').read_text(encoding='utf-8'))

    def setUp(self):
        self.m=copy.deepcopy(self.manifest)
        self.a=copy.deepcopy(self.att)
        self.l=copy.deepcopy(self.ledger)

    def audit(self):return gate.inspect_campaign(self.m,self.a,self.l)

    def satisfy_shared(self):
        for k in gate.SHARED_REQUIREMENTS:self.a['shared'][k]=v()

    def satisfy_issue(self,n):
        for k in gate.ISSUE_REQUIREMENTS:self.a['issues'][str(n)][k]=v()

    def test_six_unsent_drafts_zero_merchant_links(self):
        self.assertEqual(len(self.m['issues']),6)
        self.assertEqual([x['number'] for x in self.m['issues']],[1,2,3,4,5,6])
        self.assertTrue(all(x['publish_state']=='hold' and x['merchant_affiliate_url'] is None for x in self.m['issues']))

    def test_all_are_blocked_initially(self):
        r=self.audit()
        self.assertEqual(len(r['editions']),6)
        self.assertTrue(all(x['status']=='BLOCKED' for x in r['editions']))
        self.assertFalse(r['authorized_to_send_anything'])

    def test_editorial_is_independent_from_partner_approval(self):
        self.satisfy_shared()
        self.satisfy_issue(1)
        r=self.audit()
        self.assertEqual(r['editions'][0]['status'],'HUMAN_REVIEW_CANDIDATE_ONLY')
        self.assertEqual(r['editions'][2]['status'],'BLOCKED')
        self.assertEqual(r['editorial_review_candidates'],[1])
        self.assertFalse(r['editions'][0]['send_authorized'])

    def test_both_commercial_stay_blocked_even_if_checkboxes_all_true(self):
        self.satisfy_shared()
        for n in [3,5]:
            self.satisfy_issue(n)
            for k in gate.COMMERCIAL_REQUIREMENTS:self.a['issues'][str(n)][k]=v()
        r=self.audit()
        for n in [3,5]:
            self.assertEqual(r['editions'][n-1]['status'],'BLOCKED')
            self.assertIn('issue:approved_guide_cta_still_placeholder',r['editions'][n-1]['missing_evidence'])

    def test_fake_evidence_bool_is_not_proof(self):
        self.a['shared']['confirmed_unique_consented_audience']=True
        self.assertFalse(gate.valid_attestation(self.a['shared']['confirmed_unique_consented_audience']))

    def test_evidence_without_reviewer_blocked(self):
        x=v();x['reviewer_role']=None
        self.assertFalse(gate.valid_attestation(x))

    def test_evidence_without_reference_blocked(self):
        x=v();x['private_evidence_reference']='ok'
        self.assertFalse(gate.valid_attestation(x))

    def test_private_identifying_email_rejected(self):
        x=v();x['private_evidence_reference']='person@example.com'
        self.assertFalse(gate.valid_attestation(x))

    def test_refusing_active_merchant_link(self):
        self.m['issues'][2]['merchant_affiliate_url']='https://example.net/tracking'
        self.assertIn('edition_3_publish_or_affiliate_activation',self.audit()['structural_errors'])

    def test_refusing_early_publishing(self):
        self.m['issues'][0]['publish_state']='publish'
        self.assertIn('edition_1_publish_or_affiliate_activation',self.audit()['structural_errors'])

    def test_source_ledger_cta_mutation_blocks(self):
        self.l['entries'][5]['cta_expected']='https://example.net/bad'
        self.assertIn('issue:source_ledger_cta_not_in_sync',self.audit()['editions'][5]['missing_evidence'])

    def test_edition_mix_mutation_detected(self):
        self.m['issues'][0]['kind']='commercial-review-pending'
        self.assertIn('edition_1_type_drift',self.audit()['structural_errors'])

    def test_missing_item_or_bad_order_detected(self):
        self.m['issues'].pop()
        self.assertIn('exactly_six_editions_required',self.audit()['structural_errors'])
        self.assertIn('noncanonical_edition_ids',self.audit()['structural_errors'])

    def test_no_sending_or_wp_side_effects(self):
        r=self.audit()
        self.assertTrue(r['no_email_post_settings_list_or_tracking_changes'])
        self.assertTrue(r['human_approval_still_required'])
        self.assertTrue(all(not x['send_action_available'] for x in r['editions']))

    def test_guaranteed_hold_status(self):
        self.satisfy_shared()
        for n in (1,2,4,6):self.satisfy_issue(n)
        self.assertEqual(self.audit()['status'],'DRAFT_HOLD')
        self.assertFalse(self.audit()['authorized_to_send_anything'])

if __name__=='__main__':unittest.main()
