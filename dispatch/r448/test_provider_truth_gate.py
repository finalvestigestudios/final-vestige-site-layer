import unittest
from dataclasses import replace
from provider_truth_gate import Evidence, classify

BASE = Evidence(total=3, confirmed=3, unconfirmed_excluded=2, email_subscribed=3,
    automatic_post_emails=False, public_copy_promises_email_when_published=True,
    welcome_pdf_configured=True, welcome_received_proven=False,
    new_provider_confirmations_proven=None, merchant_email_permission_proven=False,
    validated_postal_address=False, rendered_unsubscribe_proven=False,
    native_preview_proven=False, founder_final_send_approval=False)

class ProviderGateTests(unittest.TestCase):
    def test_real_snapshot_is_hold(self):
        result = classify(BASE)
        self.assertEqual(result['release'], 'HOLD_UNSENT')
        self.assertEqual(result['email_eligible_inventory'], 3)
        self.assertEqual(result['unconfirmed_excluded'], 2)
        self.assertIsNone(result['new_confirmed_leads'])
    def test_public_expectation_mismatch_caught(self):
        self.assertIn('PUBLIC_CADENCE_EXPECTATION_MISMATCH', classify(BASE)['flags'])
    def test_matching_cadence_does_not_claim_send(self):
        changed = replace(BASE, public_copy_promises_email_when_published=False)
        self.assertNotIn('PUBLIC_CADENCE_EXPECTATION_MISMATCH', classify(changed)['flags'])
        self.assertEqual(classify(changed)['release'],'HOLD_UNSENT')
    def test_all_true_cannot_authorize_sending(self):
        changed = replace(BASE, automatic_post_emails=True, welcome_received_proven=True,
            new_provider_confirmations_proven=1, merchant_email_permission_proven=True,
            validated_postal_address=True, rendered_unsubscribe_proven=True,
            native_preview_proven=True, founder_final_send_approval=True)
        self.assertEqual(classify(changed)['release'], 'HOLD_UNSENT')
    def test_unconfirmed_not_added_to_total(self):
        self.assertEqual(classify(BASE)['confirmed_inventory'], 3)
    def test_zero_new_confirmations_different_from_unknown(self):
        x=classify(replace(BASE,new_provider_confirmations_proven=0))
        self.assertEqual(x['new_confirmed_leads'], 0)
        self.assertNotIn('NO_VERIFIED_NEW_CONFIRMED_SIGNUP_EVENT',x['flags'])
    def test_invalid_negative(self):
        with self.assertRaises(ValueError):classify(replace(BASE,total=-1))
    def test_invalid_bool_as_count(self):
        with self.assertRaises(ValueError):classify(replace(BASE,confirmed=True))
    def test_invalid_email_eligible(self):
        with self.assertRaises(ValueError):classify(replace(BASE,email_subscribed=4))
    def test_invalid_more_confirmed_than_total(self):
        with self.assertRaises(ValueError):classify(replace(BASE,total=2))
    def test_bad_new_event_over_inventory(self):
        with self.assertRaises(ValueError):classify(replace(BASE,new_provider_confirmations_proven=4))
    def test_negative_new_events(self):
        with self.assertRaises(ValueError):classify(replace(BASE,new_provider_confirmations_proven=-1))
    def test_bool_new_events_rejected(self):
        with self.assertRaises(ValueError):classify(replace(BASE,new_provider_confirmations_proven=True))
    def test_invalid_boolean_proof(self):
        with self.assertRaises(ValueError):classify(replace(BASE,merchant_email_permission_proven='yes'))
    def test_bogus_welcome_receipt(self):
        with self.assertRaises(ValueError):classify(replace(BASE,welcome_received_proven=True,welcome_pdf_configured=False))
    def test_no_identifiers_in_public_result(self):
        self.assertNotIn('email',str(classify(BASE).keys()).lower().replace('email_eligible_inventory',''))
        self.assertNotIn('@',repr(classify(BASE)))

if __name__ == '__main__':unittest.main()
