import unittest
from email.message import EmailMessage
from received_email_audit import inspect_received_eml, evaluate_private_attestations

ADDR='Final Vestige Studios, 123 Test Lane, Example City, CA 99999, USA'  # SYNTHETIC ONLY
SUB='The mind is not a camera'

def mime(subject=SUB, body='', html=None, from_name='Final Vestige Studios', to=True, unsubscribe=None):
    m=EmailMessage();m['Subject']=subject;m['From']=f'{from_name} <noreply@example.test>'
    if to:m['To']='owned-test@example.test'
    if unsubscribe:m['List-Unsubscribe']=unsubscribe
    m.set_content(body)
    if html is not None:m.add_alternative(html,subtype='html')
    return m.as_bytes()

class ReceivedProof(unittest.TestCase):
    def test_confirmation_is_not_welcome_or_campaign(self):
        x=inspect_received_eml(mime('Confirm your subscription', 'Please confirm your subscription. Confirm subscription'),expected_subject=SUB)
        self.assertEqual(x['classification'],'CONFIRMATION_ONLY')
        self.assertIn('not_received_campaign_evidence',x['evidence_gaps'])
    def test_welcome_config_not_receipt(self):
        x=inspect_received_eml(mime('Welcome','Welcome to The Dispatch. Get your Focus Fieldbook https://finalvestige.com/focus/'), expected_subject=SUB)
        self.assertEqual(x['classification'],'WELCOME_CANDIDATE')
    def test_missing_footer_not_assumed_from_provider(self):
        x=inspect_received_eml(mime(body='Read the story'),expected_subject=SUB,publisher_address=ADDR)
        self.assertFalse(x['publisher_postal_appears'])
        self.assertFalse(x['unsubscribe_structural_candidate'])
    def test_publisher_name_alone_is_insufficient(self):
        x=inspect_received_eml(mime(body='Final Vestige Studios'),expected_subject=SUB)
        self.assertFalse(x['publisher_postal_appears'])
    def test_provider_postal_address_rejected(self):
        x=inspect_received_eml(mime(body='20-22 Wenlock Street, London'),expected_subject=SUB,publisher_address='20-22 Wenlock Street, London, UK')
        self.assertFalse(x['publisher_postal_appears'])
    def test_structural_header_unsubscribe_not_functional_proof(self):
        x=inspect_received_eml(mime(body=ADDR,unsubscribe='<https://example.test/unsubscribe?id=placeholder>'),expected_subject=SUB,publisher_address=ADDR)
        self.assertTrue(x['unsubscribe_structural_candidate'])
        self.assertEqual(x['actual_optout_function'],'NOT_TESTED_BY_THIS_TOOL')
    def test_mailto_unsubscribe_accepted_only_structurally(self):
        x=inspect_received_eml(mime(body=ADDR,unsubscribe='<mailto:optout@example.test>'),expected_subject=SUB,publisher_address=ADDR)
        self.assertTrue(x['unsubscribe_structural_candidate'])
    def test_unsubscribe_anytime_without_link_not_sufficient(self):
        x=inspect_received_eml(mime(body=ADDR+' Unsubscribe anytime.'),expected_subject=SUB,publisher_address=ADDR)
        self.assertFalse(x['unsubscribe_structural_candidate'])
    def test_html_near_footer_is_detected(self):
        x=inspect_received_eml(mime(body='Plain content',html=f'<p>{ADDR}</p><a href="https://example.test/unsub">Unsubscribe</a>'),expected_subject=SUB,publisher_address=ADDR)
        self.assertTrue(x['publisher_postal_appears']);self.assertTrue(x['unsubscribe_structural_candidate'])
    def test_unapproved_mailing_deemed_hold_even_if_structural(self):
        x=inspect_received_eml(mime(body=ADDR,unsubscribe='<https://example.test/unsub>'),expected_subject=SUB,publisher_address=ADDR)
        self.assertEqual(x['release_state'],'HOLD_UNSENT')
    def test_placeholders_are_detected(self):
        x=inspect_received_eml(mime(body='[[VALID_POSTAL_ADDRESS_REQUIRED]]'),expected_subject=SUB)
        self.assertIn('unreplaced_compliance_placeholders',x['evidence_gaps'])
    def test_simulated_not_real(self):
        x=inspect_received_eml(mime(body='OFFLINE SIMULATION '+ADDR,unsubscribe='<https://example.test/unsub>'),expected_subject=SUB,publisher_address=ADDR)
        self.assertTrue(x['is_offline_simulation']);self.assertIn('offline_simulation_cannot_prove_delivery',x['evidence_gaps'])
    def test_missing_recipient_not_delivery(self):
        x=inspect_received_eml(mime(body=ADDR,to=False),expected_subject=SUB,publisher_address=ADDR)
        self.assertFalse(x['has_to_header'])
    def test_private_information_not_returned(self):
        x=inspect_received_eml(mime(body='Secret token 12345 '+ADDR,unsubscribe='<https://example.test/unsub?private=123>'),expected_subject=SUB,publisher_address=ADDR)
        self.assertNotIn('12345',str(x));self.assertNotIn('owned-test',str(x));self.assertNotIn('private=123',str(x))
    def test_unverified_attestations_fail_closed(self):
        x=evaluate_private_attestations({})
        self.assertEqual(len(x['unmet']),9);self.assertFalse(x['send_authorized_by_tool'])
    def test_fake_all_proofs_still_dont_send(self):
        d={k:{'state':'verified','proof_ref':'synthetic_proof_reference_123456'} for k in evaluate_private_attestations({})['unmet']}
        x=evaluate_private_attestations(d)
        self.assertEqual(len(x['unmet']),9);self.assertEqual(x['release_state'],'HOLD_UNSENT')
    def test_even_complete_opaque_proofs_dont_authorize(self):
        d={k:{'state':'verified','proof_ref':'private_owner_review_2026_11_14_1234'} for k in evaluate_private_attestations({})['unmet']}
        x=evaluate_private_attestations(d)
        self.assertEqual(len(x['unmet']),0);self.assertFalse(x['send_authorized_by_tool'])
    def test_case_sensitive_exact_subject(self):
        x=inspect_received_eml(mime(subject='the mind is not a camera'),expected_subject=SUB)
        self.assertFalse(x['subject_exact'])

if __name__=='__main__':unittest.main()
