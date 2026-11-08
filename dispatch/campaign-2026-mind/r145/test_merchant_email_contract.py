"""Native offline tests, no network or email. Run python -m unittest -v."""
import unittest
from pathlib import Path
from merchant_email_contract import OFFERS, REQUIRED_APPROVALS, audit, readiness
D=Path(__file__).parent
FILES={'03':'03-ZEN12-PREMIUM-ALTERNATE-UNSENT.md','05':'05-TOTAL-FOCUS-ALTERNATE-UNSENT.md'}
class CampaignTruthTests(unittest.TestCase):
    def draft(self,k):return (D/FILES[k]).read_text('utf-8')
    def test_both_issue_types_reserved(self):self.assertEqual(set(OFFERS),{'03','05'})
    def test_both_unapproved(self):
        for k in OFFERS:self.assertEqual(readiness(k,self.draft(k),{})['release'],'HOLD_UNSENT')
    def test_both_merchant_blocked(self):
        for k in OFFERS:self.assertEqual(readiness(k,self.draft(k),{})['merchant'],'HOLD_MERCHANT')
    def test_official_sources(self):
        self.assertIn('https://zen12.com/?no-popup=1',self.draft('03'))
        self.assertIn('https://hypnosislive.com/mental-skills/total-focus',self.draft('05'))
    def test_no_seller_price_in_body(self):
        for k in OFFERS:self.assertNotRegex(self.draft(k),r'\$\d')
    def test_no_active_affiliate_url(self):
        for k in OFFERS:
            self.assertNotRegex(self.draft(k),r'(?i)ref=\d+|aff_id=|affiliate_id=|utm_')
    def test_no_unsupported_miracle_promises(self):
        for k in OFFERS:self.assertNotIn('unsupported_claim_language',readiness(k,self.draft(k),{})['blockers'])
    def test_explicit_product_identity(self):
        for k,(name,_) in OFFERS.items():self.assertIn(name,self.draft(k))
    def test_one_primary_cta_target_appears_twice(self):
        for k,(_,target) in OFFERS.items():self.assertEqual(self.draft(k).count(target),2)
    def test_disclosure_in_both(self):
        for k in OFFERS:self.assertIn('Commercial disclosure',self.draft(k))
    def test_removal_of_disclosure_detected(self):
        k='03'; c=self.draft(k).replace('Commercial disclosure','Editorial note').replace('may earn a commission','might receive credit')
        self.assertIn('disclosure_missing',readiness(k,c,{})['blockers'])
    def test_wrong_product_rejected(self):
        self.assertIn('specific_product_identity_missing',readiness('05',self.draft('05').replace('Hypnosis Live — Total Focus','Other course'),{})['blockers'])
    def test_missing_cta_rejected(self):
        c=self.draft('03').replace(OFFERS['03'][1],'')
        self.assertIn('expected_pending_guide_sentinel_missing',readiness('03',c,{})['blockers'])
    def test_duplicate_cta_rejected(self):
        c=self.draft('05')+'\n'+OFFERS['05'][1]
        self.assertIn('unexpected_number_of_primary_guide_mentions',readiness('05',c,{})['blockers'])
    def test_guaranteed_claim_rejected(self):
        c=self.draft('03')+'\nGuaranteed focus for everyone.'
        self.assertIn('unsupported_claim_language',readiness('03',c,{})['blockers'])
    def test_unverified_all_false(self):
        b=readiness('03',self.draft('03'),{})['blockers']
        self.assertEqual(len([x for x in b if x.startswith('unverified:')]),len(REQUIRED_APPROVALS))
    def test_truthy_string_rejected(self):
        b=readiness('05',self.draft('05'),{'promotional_email_channel_permitted':'true'})['blockers']
        self.assertIn('unverified:promotional_email_channel_permitted',b)
    def test_truthy_number_rejected(self):
        b=readiness('05',self.draft('05'),{'promotional_email_channel_permitted':1})['blockers']
        self.assertIn('unverified:promotional_email_channel_permitted',b)
    def test_explicit_true_cannot_override_draft(self):
        a={k:True for k in REQUIRED_APPROVALS}
        b=readiness('03',self.draft('03'),a)
        self.assertEqual(b['release'],'HOLD_UNSENT')
        self.assertIn('source_only_hard_stop',b['blockers'])
    def test_postal_placeholder_stops(self):
        self.assertIn('postal_address_placeholder',readiness('05',self.draft('05'),{})['blockers'])
    def test_unsubscribe_placeholder_stops(self):
        self.assertIn('unsubscribe_placeholder',readiness('03',self.draft('03'),{})['blockers'])
    def test_no_real_revenue_metrics(self):
        a=audit(D,{})
        self.assertIsNone(a['realized_net_revenue_per_1000'])
        self.assertIsNone(a['verified_paid_sales'])
    def test_no_emails_were_sent_by_auditor(self):
        self.assertEqual(audit(D,{})['email_sends'],'NOT_PERFORMED')
    def test_bad_offer_rejected(self):
        with self.assertRaises(ValueError):readiness('00','',{})
    def test_nonobject_attestations_rejected(self):
        with self.assertRaises(ValueError):readiness('03',self.draft('03'),[])
    def test_injected_tracking_rejected(self):
        c=self.draft('03')+'\nhttps://seller.example/?affiliate_id=123'
        self.assertIn('unapproved_tracking_or_merchant_identifier',readiness('03',c,{})['blockers'])
if __name__=='__main__':unittest.main()
