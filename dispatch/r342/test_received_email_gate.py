import unittest
from email.message import EmailMessage
from received_email_gate import evaluate_mime

VALID_ADDR = 'Final Vestige Studios, 123 Example Street, Sample City, CA 00000'
# Address above is deliberately fictional test fixture and MUST NOT be placed in real copy.

def fixture(edition='01', *, subject='The Door That Hid a Stranger', sender='Final Vestige Studios <no-reply@wordpress.com>', disclosure=True, postal=True, unsub=True, html=True, plain=True):
    msg=EmailMessage(); msg['Subject']=subject;msg['From']=sender;msg['To']='synthetic@example.test'
    main=f'<a href="https://finalvestige.com/2026/11/02/change-blindness/">Read the investigation</a>'
    leave='<a href="https://wordpress.com/notifications/subscriptions/?unsubscribe=synthetic">Unsubscribe</a>' if unsub else ''
    footer=(VALID_ADDR if postal else '[Publisher postal address pending]')
    offer='If you buy through the guide, Final Vestige may earn a commission. Seller claims are not independent proof.' if disclosure else ''
    body=f'{main} {offer} {footer} {leave}'
    if plain: msg.set_content('The Dispatch\n'+body)
    else: msg.set_content('')
    if html: msg.add_alternative('<html><body><p>'+body+'</p></body></html>',subtype='html')
    return msg.as_bytes()

class Safety(unittest.TestCase):
    def test_all_six_are_held_even_perfect_synthetic(self):
        for edition in ('01','02','03','04','05','06'):
            with self.subTest(edition=edition):
                result=evaluate_mime(fixture(edition),edition)
                self.assertEqual(result['decision'],'HOLD_UNSENT')
                self.assertFalse(result['send_authorized'])
                self.assertIn('NOT_AUTHENTIC_RECEIVED_EMAIL',result['gate_failures'])
    def test_fake_live_provenance_never_authorizes(self):
        checks={k:True for k in ['founder_final_approval','native_jetpack_preview_attested','fv_postal_ownership_verified','unsubscribe_function_tested','provider_confirmed_eligible_recipients','named_affiliate_approval','email_channel_permission','issued_tracking_link','guide_live_and_approved','merchant_claims_checked']}
        for e in ('01','03','05'):
            r=evaluate_mime(fixture(e),e,provenance='LIVE_RECEIVED',approvals=checks)
            self.assertFalse(r['send_authorized'])
            self.assertTrue(r['provenance_is_self_attested'])
    def test_incomplete_proofs_hard_fail(self):
        r=evaluate_mime(fixture('03'),'03')
        self.assertTrue(any('EMAIL_CHANNEL_PERMISSION' in s for s in r['gate_failures']))
    def test_missing_disclosure_detected(self):
        r=evaluate_mime(fixture('05',disclosure=False),'05')
        self.assertIn('NEAR_OFFER_DISCLOSURE_MISSING',r['gate_failures'])
    def test_missing_unsub_detected(self):
        r=evaluate_mime(fixture(unsub=False),'01')
        self.assertIn('OPT_OUT_LINK_MISSING',r['gate_failures'])
    def test_missing_postal_detected(self):
        r=evaluate_mime(fixture(postal=False),'01')
        self.assertIn('POSTAL_PLACEHOLDER',r['gate_failures'])
    def test_bad_sender_detected(self):
        r=evaluate_mime(fixture(sender='Automattic <donotreply@wordpress.com>'),'01')
        self.assertIn('SENDER_IDENTITY_UNVERIFIED',r['gate_failures'])
    def test_invalid_subject_detected(self):
        r=evaluate_mime(fixture(subject='[SUBJECT]'),'01')
        self.assertIn('SUBJECT_INVALID',r['gate_failures'])
    def test_not_a_real_email_doesnt_reveal_address(self):
        r=evaluate_mime(fixture(),'01')
        self.assertNotIn('synthetic@example.test',str(r))
        self.assertNotIn('123 Example Street',str(r))
    def test_oversize_and_wrong_edition_rejected(self):
        with self.assertRaises(ValueError): evaluate_mime(b'x'*1000001,'01')
        with self.assertRaises(ValueError): evaluate_mime(fixture(),'07')

if __name__=='__main__':unittest.main()
