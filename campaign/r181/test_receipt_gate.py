"""All fixtures are fabricated and never represent a real received email."""
import unittest
from email.message import EmailMessage
from receipt_gate import analyze


def fixture(plain="Hello", html="<p>Hello</p>", unsub=True):
    msg = EmailMessage()
    msg['Subject'] = 'Synthetic test only'
    msg['From'] = 'fake-sender@example.invalid'
    msg['To'] = 'fake-reader@example.invalid'
    if unsub:
        msg['List-Unsubscribe'] = '<https://example.invalid/unsub>'
    msg.set_content(plain)
    msg.add_alternative(html, subtype='html')
    return msg.as_bytes()


class GateTests(unittest.TestCase):
    def test_no_email_release_even_with_credible_headers(self):
        x=analyze(fixture(),commercial=True)
        self.assertEqual(x['release_decision'],'HOLD_UNSENT')
        self.assertFalse(x['founder_campaign_send_approval'])
        self.assertFalse(x['native_jetpack_rendering_verified'])
        self.assertFalse(x['merchant_named_email_permission_verified'])

    def test_no_exposure_of_recipient_identifiers(self):
        results=str(analyze(fixture(plain='secrets@example.invalid 123 Fake St.'),commercial=True))
        self.assertNotIn('secrets@example.invalid', results)
        self.assertNotIn('fake-reader',results)
        self.assertNotIn('Fake St.',results)

    def test_hardstop_placeholders_detected(self):
        self.assertTrue(analyze(fixture('[[VALID_POSTAL_ADDRESS_REQUIRED]]'))['contains_unresolved_placeholders'])

    def test_unsubscribe_header_only_is_not_functional_proof(self):
        x=analyze(fixture())
        self.assertTrue(x['has_unsubscribe_indicator_not_function_test'])
        self.assertFalse(x['unsubscribe_functionally_verified'])

    def test_no_unsubscribe_indicator(self):
        self.assertFalse(analyze(fixture('Hi','<p>Hi</p>',unsub=False))['has_unsubscribe_indicator_not_function_test'])

    def test_hidden_disclosure_is_not_visible_indicator(self):
        x=analyze(fixture('hello','<p>Offer</p><div style="display:none">may earn commission</div>',unsub=False),commercial=True)
        self.assertFalse(x['commercial_disclosure_indicator_not_adjacency_proof'])

    def test_visible_disclosure_still_not_authorization(self):
        x=analyze(fixture('Hello','<p>Offer. If you buy through our guide, we may earn a commission.</p>',unsub=False), commercial=True)
        self.assertTrue(x['commercial_disclosure_indicator_not_adjacency_proof'])
        self.assertFalse(x['merchant_named_email_permission_verified'])

    def test_no_real_publisher_postal_proof_from_fake_address(self):
        x=analyze(fixture('Hello','<footer>44 Example Street</footer>'))
        self.assertTrue(x['has_postal_appearance_not_publisher_proof'])
        self.assertFalse(x['publisher_postal_address_attested'])

    def test_multipart_attachments_not_parsed_as_text(self):
        m=EmailMessage();m['From']='x@example.invalid';m['To']='y@example.invalid';m['Subject']='Test';m.set_content('hello')
        m.add_attachment('[[INVALID]]',subtype='plain',filename='attachment.txt')
        self.assertFalse(analyze(m.as_bytes())['contains_unresolved_placeholders'])

    def test_no_false_confirmed_signup_or_welcome(self):
        x=analyze(fixture('Welcome to the Fieldbook','<p>Confirmed subscription!</p>'))
        self.assertFalse(x['provider_confirmed_subscriber_and_consent'])
        self.assertFalse(x['fieldbook_welcome_received_verified'])


if __name__=='__main__': unittest.main()
