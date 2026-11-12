import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import unittest
from datetime import datetime, timedelta, timezone
from broadcast_cohort_gate import SyntheticMember, hypothetical_broadcast_matrix, review_notification, digest_readout
T=datetime(2027, 1, 1, 12, tzinfo=timezone.utc) # SYNTHETIC; no campaign schedule

def member(s='subscribed', confirm=T, **kwargs):
    return SyntheticMember('synthetic_001', confirm, s, **kwargs)

class BroadcastVsDrip(unittest.TestCase):
    def test_exact_six_and_mix(self):
        self.assertEqual(len(hypothetical_broadcast_matrix([member()],T)['synthetic_001']), 6)
    def test_before_first_is_held_for_editorial(self):
        self.assertEqual(hypothetical_broadcast_matrix([member()],T)['synthetic_001'][0],'eligible_but_held')
    def test_late_signup_not_backfilled(self):
        rows=hypothetical_broadcast_matrix([member(confirm=T+timedelta(days=21))],T)['synthetic_001']
        self.assertEqual(rows[:3], ['joined_after_publication']*3)
        self.assertEqual(rows[3], 'eligible_but_held')
    def test_commercial_kept_separately(self):
        rows=hypothetical_broadcast_matrix([member()],T)['synthetic_001']
        self.assertEqual(rows[2], 'merchant_or_consent_hold')
        self.assertEqual(rows[4], 'merchant_or_consent_hold')
    def test_a_late_subscriber_cannot_be_claimed_six_of_six(self):
        rows=hypothetical_broadcast_matrix([member(confirm=T+timedelta(days=28))],T)['synthetic_001']
        self.assertEqual(sum(x=='joined_after_publication' for x in rows),4)
    def test_no_confirmation(self):
        self.assertEqual(review_notification(member(confirm=None),T,'editorial'),'unverified_confirmation')
    def test_no_reader_only(self):
        self.assertEqual(review_notification(member(s='reader_only'),T,'editorial'),'not_verified_email_eligible')
    def test_no_pending(self):
        self.assertEqual(review_notification(member(s='pending'),T,'editorial'),'not_verified_email_eligible')
    def test_no_paused(self):
        self.assertEqual(review_notification(member(s='paused'),T,'editorial'),'not_verified_email_eligible')
    def test_no_bounced(self):
        self.assertEqual(review_notification(member(s='bounced'),T,'editorial'),'not_verified_email_eligible')
    def test_no_unknown(self):
        self.assertEqual(review_notification(member(s='unknown'),T,'editorial'),'not_verified_email_eligible')
    def test_no_unsubscribed(self):
        self.assertEqual(review_notification(member(s='unsubscribed'),T,'editorial'),'not_verified_email_eligible')
    def test_temporal_optout(self):
        self.assertEqual(review_notification(member(opted_out_at=T),T,'editorial'),'opted_out')
    def test_optout_after_published_does_not_retroactively_change(self):
        self.assertEqual(review_notification(member(opted_out_at=T+timedelta(days=1)),T,'editorial'),'eligible_but_held')
    def test_merchant_all_rights_but_no_legal_footer(self):
        x=review_notification(member(consent_for_commercial=True),T,'commercial',email_rights=True,verified_live_guide=True)
        self.assertEqual(x,'eligible_but_held')
    def test_merchant_rights_missing_even_if_approved(self):
        x=review_notification(member(consent_for_commercial=True),T,'commercial',final_send_approval=True,physical_footer=True,working_unsubscribe=True,verified_live_guide=True)
        self.assertEqual(x,'merchant_or_consent_hold')
    def test_merchant_guide_missing(self):
        x=review_notification(member(consent_for_commercial=True),T,'commercial',email_rights=True,final_send_approval=True,physical_footer=True,working_unsubscribe=True)
        self.assertEqual(x,'merchant_or_consent_hold')
    def test_no_fabricated_ready_just_theoretical(self):
        x=review_notification(member(),T,'editorial',final_send_approval=True,physical_footer=True,working_unsubscribe=True)
        self.assertEqual(x,'theoretically_eligible_not_sent')
    def test_sender_approval_alone_cannot_pass(self):
        self.assertEqual(review_notification(member(),T,'editorial',final_send_approval=True),'eligible_but_held')
    def test_unconfirmed_after_date(self):
        self.assertEqual(review_notification(member(confirm=T+timedelta(days=1)),T,'commercial'),'joined_after_publication')
    def test_duplicate_synthetic_members(self):
        with self.assertRaises(ValueError):hypothetical_broadcast_matrix([member(), member()],T)
    def test_refuse_actual_email_id(self):
        with self.assertRaises(ValueError):review_notification(SyntheticMember('person@example.com',T,'subscribed'),T,'editorial')
    def test_tzless_date(self):
        with self.assertRaises(ValueError):review_notification(member(),datetime(2027,1,1),'editorial')
    def test_unsupported_status(self):
        with self.assertRaises(ValueError):review_notification(member(s='sent'),T,'editorial')
    def test_unsupported_kind(self):
        with self.assertRaises(ValueError):review_notification(member(),T,'affiliate_unknown')
    def test_negative_interval(self):
        with self.assertRaises(ValueError):hypothetical_broadcast_matrix([member()],T,spacing_days=0)
    def test_digest_is_not_delivery(self):
        m=hypothetical_broadcast_matrix([member()],T)
        self.assertEqual(digest_readout(m)['merchant_or_consent_hold'],2)

if __name__=='__main__':unittest.main()
